import datetime as dt
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import requests

INST = {"usa500idxusd": "S&P 500", "usatechidxusd": "Nasdaq 100"}
BREAKOUT_BARS = 55
STOP_BARS = 27
RR = 2.0
MIN_H4_BARS = 60
NY_TZ = "America/New_York"
DATA_DIR = Path("dl")
STATE_FILE = Path("state.json")


def utc_now():
    return pd.Timestamp.now(tz="UTC")


def as_utc(value):
    ts = pd.Timestamp(value)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def iso_utc(value):
    return as_utc(value).isoformat().replace("+00:00", "Z")


def price(value):
    return f"{float(value):.2f}"


def fresh_instrument_state():
    return {
        "position": None,
        "last_processed_h4_bar_utc": None,
        "last_processed_outcome": None,
        "last_exit": None,
    }


def load_state():
    if not STATE_FILE.exists():
        print("STATE: state.json belum ada; memulai dengan state kosong.", flush=True)
        state = {"schema_version": 1, "instruments": {}}
    else:
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RuntimeError(f"state.json rusak/tidak terbaca: {exc}") from exc
        if not isinstance(state, dict) or not isinstance(state.get("instruments"), dict):
            raise RuntimeError("Struktur state.json tidak valid; state tidak di-reset otomatis.")
        if state.get("schema_version", 1) != 1:
            raise RuntimeError(f"Versi state.json tidak didukung: {state.get('schema_version')!r}")
        state["schema_version"] = 1

    records = state.setdefault("instruments", {})
    for inst in INST:
        rec = records.setdefault(inst, fresh_instrument_state())
        if not isinstance(rec, dict):
            raise RuntimeError(f"State instrumen {inst} bukan object.")
        for key, default in fresh_instrument_state().items():
            rec.setdefault(key, default)
        pos = rec.get("position")
        if pos is not None:
            required = {"entry_time_utc", "entry", "sl", "tp", "signal_bar_utc"}
            missing = required.difference(pos)
            if missing:
                raise RuntimeError(f"Posisi {inst} kehilangan field: {sorted(missing)}")
            for key in ("entry", "sl", "tp"):
                if not math.isfinite(float(pos[key])):
                    raise RuntimeError(f"Posisi {inst} memiliki {key} tidak valid.")
            as_utc(pos["entry_time_utc"])
    return state


def save_state(state):
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(STATE_FILE)
    print(f"STATE: state.json disimpan ({STATE_FILE.stat().st_size} bytes).", flush=True)


def start_date_for(inst_state):
    start = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=45)
    pos = inst_state.get("position")
    if pos:
        entry_date = as_utc(pos["entry_time_utc"]).date()
        start = min(start, entry_date - dt.timedelta(days=2))
    return start


def parse_csv(path, inst):
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ValueError(f"CSV tidak bisa dibaca: {type(exc).__name__}: {exc}") from exc
    original_cols = [str(c) for c in df.columns]
    print(f"CSV HEADER {inst}: {original_cols}", flush=True)
    if df.empty:
        raise ValueError("CSV kosong atau hanya berisi header.")

    df.columns = [str(c).replace("\ufeff", "").strip().lower() for c in df.columns]
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Kolom wajib hilang {sorted(missing)}; header aktual={original_cols}")

    raw = df["timestamp"].astype(str).str.strip()
    print(f"CSV TIMESTAMP SAMPLE {inst}: first={raw.iloc[0]!r}; last={raw.iloc[-1]!r}", flush=True)
    numeric = pd.to_numeric(df["timestamp"], errors="coerce")
    if numeric.notna().mean() > 0.95:
        if numeric.isna().any():
            raise ValueError("Timestamp tampak numerik tetapi ada nilai timestamp rusak.")
        median_abs = float(numeric.abs().median())
        if median_abs >= 1e11:
            unit, label = "ms", "Unix milliseconds"
        elif median_abs >= 1e8:
            unit, label = "s", "Unix seconds"
        else:
            raise ValueError(f"Skala timestamp numerik tidak dikenali: median abs={median_abs}")
        index = pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
        print(f"CSV TIMESTAMP FORMAT {inst}: {label} (unit={unit}).", flush=True)
    else:
        index = pd.to_datetime(raw, utc=True, errors="coerce")
        print(f"CSV TIMESTAMP FORMAT {inst}: date/time text parsed as UTC.", flush=True)
    if index.isna().any():
        examples = raw[index.isna()].head(3).tolist()
        raise ValueError(f"Timestamp gagal diparse; contoh={examples}")

    bars = df[["open", "high", "low", "close"]].copy()
    for col in bars.columns:
        bars[col] = pd.to_numeric(bars[col], errors="coerce")
        if bars[col].isna().any() or not bars[col].map(math.isfinite).all():
            raise ValueError(f"OHLC {col} berisi nilai kosong/non-numerik/tak hingga.")
    bars.index = pd.DatetimeIndex(index, name="timestamp_utc")
    bars = bars.sort_index()
    duplicates = int(bars.index.duplicated(keep="last").sum())
    if duplicates:
        print(f"CSV WARNING {inst}: menghapus {duplicates} timestamp duplikat (memakai bar terakhir).", flush=True)
        bars = bars.loc[~bars.index.duplicated(keep="last")]
    if bars.empty:
        raise ValueError("CSV tidak memiliki bar OHLC valid.")
    print(
        f"CSV VALID {inst}: bars={len(bars)}; UTC={bars.index[0].isoformat()}..{bars.index[-1].isoformat()}; "
        f"NY={bars.index[0].tz_convert(NY_TZ)}..{bars.index[-1].tz_convert(NY_TZ)}",
        flush=True,
    )
    return bars


def fetch_h1(inst, inst_state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{inst}.csv"
    start = start_date_for(inst_state)
    command = [
        "npx", "--yes", "dukascopy-node",
        "-i", inst, "-from", str(start), "-to", "now",
        "-t", "h1", "-p", "bid", "-utc", "0", "-f", "csv", "-fl",
        "-dir", str(DATA_DIR), "-fn", inst,
        "-bs", "3", "-bp", "2000", "-r", "5", "-re", "-rp", "5000",
    ]
    last_error = "unknown download error"
    patch = Path("dukascopy_fetch_patch.cjs").resolve()
    for attempt in range(1, 4):
        path.unlink(missing_ok=True)
        if not patch.is_file():
            last_error = f"patch downloader tidak ditemukan: {patch}"
            print(f"DOWNLOAD ERROR {inst} attempt {attempt}/3: {last_error}", flush=True)
        else:
            env = os.environ.copy()
            opts = env.get("NODE_OPTIONS", "").strip()
            env["NODE_OPTIONS"] = f"{opts} --require={patch}".strip()
            print(
                f"DOWNLOAD {inst}: attempt {attempt}/3; from={start}; timeframe=H1; price=bid; UTC offset=0",
                flush=True,
            )
            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, check=False, env=env)
                if result.stdout:
                    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n", flush=True)
                if result.returncode != 0:
                    last_error = f"dukascopy-node exit code {result.returncode}"
                elif not path.is_file():
                    last_error = f"CSV tidak dibuat: {path}"
                elif path.stat().st_size == 0:
                    last_error = f"CSV kosong: {path}"
                else:
                    try:
                        return parse_csv(path, inst)
                    except Exception as exc:
                        last_error = f"CSV invalid: {type(exc).__name__}: {exc}"
            except Exception as exc:
                last_error = f"downloader gagal dijalankan: {type(exc).__name__}: {exc}"
            print(f"DOWNLOAD ERROR {inst} attempt {attempt}/3: {last_error}", flush=True)
        if attempt < 3:
            pause = 10 * attempt
            print(f"Retry {inst} dalam {pause} detik.", flush=True)
            time.sleep(pause)
    raise RuntimeError(f"Gagal download/parse {inst} setelah 3 percobaan. Error terakhir: {last_error}")


def to_h4(h1):
    local = h1.copy()
    local.index = local.index.tz_convert(NY_TZ)
    return local.resample("4h", offset="1h", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    ).dropna(subset=["open", "high", "low", "close"])


def completed_h4(h4, now):
    close_utc = h4.index.tz_convert("UTC") + pd.Timedelta(hours=4)
    return h4.loc[close_utc <= now].copy()


def diagnostics(h4):
    n = len(h4)
    if n == 0:
        return {"h4_count": n, "close_ny": "N/A", "close_value": "N/A", "prior_high": "N/A"}
    label = h4.index[-1]
    close_time = (label.tz_convert("UTC") + pd.Timedelta(hours=4)).tz_convert(NY_TZ)
    prior_high = price(h4["high"].iloc[-1 - BREAKOUT_BARS:-1].max()) if n > BREAKOUT_BARS else "N/A"
    return {
        "h4_count": n,
        "close_ny": close_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "close_value": price(h4["close"].iloc[-1]),
        "prior_high": prior_high,
    }


def error_verdict(inst, name, error, h4_count="N/A", close_ny="N/A", close_value="N/A", prior_high="N/A"):
    print(
        f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={close_value} | "
        f"high_55_previous={prior_high} | H4_bars={h4_count} | ERROR={error} | VERDICT=ERROR",
        flush=True,
    )


def marker_for(inst, label_utc):
    return f"R191-{inst}-{label_utc.strftime('%Y%m%dT%H%M%SZ')}"


def signal_issue(inst, name, marker, signal_close, entry_time, entry, stop, target, prev_high, close_value):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER") or (repo.split("/", 1)[0] if repo else "")
    if not token or not repo:
        raise RuntimeError("GH_TOKEN/GITHUB_TOKEN atau GITHUB_REPOSITORY tidak tersedia untuk membuat issue.")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(
        "https://api.github.com/search/issues",
        headers=headers,
        params={"q": f"repo:{repo} is:issue in:title {marker}", "per_page": 100},
        timeout=20,
    )
    response.raise_for_status()
    existing = next((x for x in response.json().get("items", []) if marker in x.get("title", "")), None)
    if existing:
        url = existing.get("html_url", "")
        print(f"ISSUE DEDUPE {inst}: marker {marker} sudah ada: {url}", flush=True)
        return url, False

    signal_ny = signal_close.tz_convert(NY_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    entry_ny = entry_time.tz_convert(NY_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    body = (
        f"@{owner} R191 LONG baru\n\n"
        f"- Instrumen: {inst} ({name})\n"
        f"- Signal H4 close NY: {signal_ny}\n"
        f"- Entry open bar H4 i+1: {price(entry)} pada {entry_ny} NY\n"
        f"- SL: {price(stop)}\n- TP: {price(target)}\n"
        f"- Close bar sinyal: {price(close_value)}\n"
        f"- High maksimum 55 bar H4 sebelumnya: {price(prev_high)}\n"
        f"- Signal ID: {marker}\n\n"
        "LONG-only. Exit dipantau memakai OHLC H1 bid; SL diperiksa lebih dahulu. "
        "Gap menembus SL diisi pada open. Tanpa time-stop."
    )
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers=headers,
        json={"title": f"R191 LONG | {name} | {marker}", "body": body},
        timeout=20,
    )
    response.raise_for_status()
    url = response.json().get("html_url", "")
    print(f"ISSUE CREATED {inst}: {url}", flush=True)
    return url, True


def advance_position(inst, name, state, h1, now, before=None):
    pos = state.get("position")
    if not pos:
        return None
    entry_time = as_utc(pos["entry_time_utc"])
    if h1.empty:
        raise RuntimeError(f"Tidak ada bar H1 untuk memantau posisi {inst}.")
    if h1.index.min() > entry_time:
        raise RuntimeError(
            f"Data H1 {inst} mulai setelah entry ({h1.index.min().isoformat()} > {entry_time.isoformat()}); "
            "menolak menebak exit."
        )
    mask = (h1.index >= entry_time) & (h1.index <= now)
    if before is not None:
        mask &= h1.index < before
    stop, target = float(pos["sl"]), float(pos["tp"])
    for bar_time, bar in h1.loc[mask].iterrows():
        op, hi, lo = float(bar["open"]), float(bar["high"]), float(bar["low"])
        # SL takes priority; an opening gap through SL fills at the open.
        if lo <= stop or op <= stop:
            fill = op if op <= stop else stop
            reason = "SL_GAP_OPEN" if op <= stop else "SL"
        elif hi >= target:
            fill, reason = target, "TP"
        else:
            continue
        record = {
            "entry_time_utc": pos["entry_time_utc"], "entry": float(pos["entry"]),
            "sl": stop, "tp": target, "exit_bar_start_utc": iso_utc(bar_time),
            "exit_price": float(fill), "reason": reason, "signal_bar_utc": pos["signal_bar_utc"],
        }
        state["position"] = None
        state["last_exit"] = record
        print(
            f"POSITION EXIT {name} ({inst}): reason={reason}; H1_start_UTC={iso_utc(bar_time)}; fill={price(fill)}",
            flush=True,
        )
        return record
    return None


def active_text(rec):
    pos = rec.get("position")
    if not pos:
        return ""
    return f" | POSISI_AKTIF entry={price(pos['entry'])} SL={price(pos['sl'])} TP={price(pos['tp'])}"


def analyze(inst, name, h1, h4_all, h4, rec, now):
    n = len(h4)
    if n < MIN_H4_BARS:
        raise RuntimeError(f"HARD ERROR: hanya {n} bar H4 lengkap; minimum {MIN_H4_BARS}.")

    label = h4.index[-1]
    label_utc = label.tz_convert("UTC")
    close_time = label_utc + pd.Timedelta(hours=4)
    close_ny = close_time.tz_convert(NY_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    close_value = float(h4["close"].iloc[-1])
    prior_high = float(h4["high"].iloc[-1 - BREAKOUT_BARS:-1].max())
    stop = float(h4["low"].iloc[-STOP_BARS:].min())
    breakout = close_value > prior_high
    bar_key = iso_utc(label_utc)
    new_bar = rec.get("last_processed_h4_bar_utc") != bar_key
    marker = marker_for(inst, label_utc)

    if not breakout:
        if new_bar:
            rec["last_processed_h4_bar_utc"] = bar_key
            rec["last_processed_outcome"] = "NO_SIGNAL"
        exit_record = advance_position(inst, name, rec, h1, now)
        suffix = active_text(rec)
        if exit_record:
            suffix += f" | EXIT={exit_record['reason']}"
        return (
            f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={price(close_value)} | "
            f"high_55_previous={price(prior_high)} | H4_bars={n} | VERDICT=NO SIGNAL{suffix}"
        )

    if not new_bar:
        exit_record = advance_position(inst, name, rec, h1, now)
        outcome = rec.get("last_processed_outcome")
        verdict = (
            "NO SIGNAL (setup sebelumnya diabaikan karena posisi aktif)"
            if outcome == "IGNORED_ACTIVE_POSITION"
            else "SINYAL LONG (bar sudah diproses; issue/entry tidak digandakan)"
        )
        suffix = active_text(rec)
        if exit_record:
            suffix += f" | EXIT={exit_record['reason']}"
        return (
            f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={price(close_value)} | "
            f"high_55_previous={price(prior_high)} | H4_bars={n} | VERDICT={verdict}{suffix}"
        )

    # Any prior position must be closed before the signal boundary to permit a new entry.
    advance_position(inst, name, rec, h1, now, before=close_time)
    if rec.get("position") is not None:
        rec["last_processed_h4_bar_utc"] = bar_key
        rec["last_processed_outcome"] = "IGNORED_ACTIVE_POSITION"
        exit_record = advance_position(inst, name, rec, h1, now)
        suffix = active_text(rec)
        if exit_record:
            suffix += f" | EXIT={exit_record['reason']}"
        return (
            f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={price(close_value)} | "
            f"high_55_previous={price(prior_high)} | H4_bars={n} | "
            f"VERDICT=NO SIGNAL (setup diabaikan: posisi masih aktif saat signal time){suffix}"
        )

    # Bar i+1 must exist. Its open is used for entry; its high/low/close never form the signal.
    following = h4_all.loc[h4_all.index.tz_convert("UTC") > label_utc]
    if following.empty:
        return (
            f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={price(close_value)} | "
            f"high_55_previous={price(prior_high)} | H4_bars={n} | "
            "VERDICT=SINYAL LONG, menunggu open bar H4 i+1"
        )
    next_label = following.index[0]
    entry_time = next_label.tz_convert("UTC")
    entry = float(following["open"].iloc[0])
    if not math.isfinite(entry) or entry_time > now:
        return (
            f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={price(close_value)} | "
            f"high_55_previous={price(prior_high)} | H4_bars={n} | "
            "VERDICT=SINYAL LONG, open bar H4 i+1 belum tersedia/valid; akan dicoba ulang"
        )

    target = entry + RR * (entry - stop)
    if entry <= stop:
        print(
            f"R191 WARNING {inst}: entry ({price(entry)}) <= SL ({price(stop)}); "
            "rumus SL/TP dipertahankan persis sesuai instruksi.",
            flush=True,
        )
    issue_url, created = signal_issue(
        inst, name, marker, close_time, entry_time, entry, stop, target, prior_high, close_value
    )
    rec["position"] = {
        "entry_time_utc": iso_utc(entry_time), "entry": entry, "sl": stop, "tp": target,
        "signal_bar_utc": iso_utc(label_utc), "signal_close_time_utc": iso_utc(close_time),
        "signal_id": marker, "issue_url": issue_url,
    }
    rec["last_processed_h4_bar_utc"] = bar_key
    rec["last_processed_outcome"] = "SIGNAL_CREATED"
    exit_record = advance_position(inst, name, rec, h1, now)
    verdict = "SINYAL LONG (issue baru)" if created else "SINYAL LONG (issue sebelumnya ditemukan; duplikat dicegah)"
    suffix = f" | entry_open_H4_i+1={price(entry)} | SL={price(stop)} | TP={price(target)} | issue={issue_url}"
    if exit_record:
        suffix += f" | posisi langsung tercatat EXIT={exit_record['reason']}"
    else:
        suffix += active_text(rec)
    return (
        f"VERDICT | {name} ({inst}) | H4_last_close_NY={close_ny} | close={price(close_value)} | "
        f"high_55_previous={price(prior_high)} | H4_bars={n} | VERDICT={verdict}{suffix}"
    )


def main():
    try:
        state = load_state()
    except Exception as exc:
        for inst, name in INST.items():
            error_verdict(inst, name, f"STATE ERROR: {type(exc).__name__}: {exc}")
        raise SystemExit(1)

    fetched, errors, prepared = {}, {}, {}
    for inst, name in INST.items():
        try:
            fetched[inst] = fetch_h1(inst, state["instruments"][inst])
        except Exception as exc:
            errors[inst] = f"{type(exc).__name__}: {exc}"
            print(f"HARD ERROR {name} ({inst}): {errors[inst]}", flush=True)
            error_verdict(inst, name, errors[inst])

    now = utc_now()
    for inst, name in INST.items():
        if inst not in fetched:
            continue
        try:
            all_h4 = to_h4(fetched[inst])
            closed = completed_h4(all_h4, now)
            if len(closed) < MIN_H4_BARS:
                errors[inst] = (
                    f"HARD ERROR: hanya {len(closed)} bar H4 yang sudah close; minimum {MIN_H4_BARS}."
                )
                diag = diagnostics(closed)
                error_verdict(inst, name, errors[inst], diag["h4_count"], diag["close_ny"],
                              diag["close_value"], diag["prior_high"])
                continue
            prepared[inst] = (fetched[inst], all_h4, closed)
        except Exception as exc:
            errors[inst] = f"H4 processing error: {type(exc).__name__}: {exc}"
            error_verdict(inst, name, errors[inst])

    for inst, name in INST.items():
        if inst not in prepared:
            continue
        h1, all_h4, closed = prepared[inst]
        try:
            print(analyze(inst, name, h1, all_h4, closed, state["instruments"][inst], now), flush=True)
        except Exception as exc:
            errors[inst] = f"scanner processing error: {type(exc).__name__}: {exc}"
            diag = diagnostics(closed)
            error_verdict(inst, name, errors[inst], diag["h4_count"], diag["close_ny"],
                          diag["close_value"], diag["prior_high"])

    try:
        save_state(state)
    except Exception as exc:
        errors["state.json"] = f"save failed: {type(exc).__name__}: {exc}"
        print(f"HARD ERROR menyimpan state.json: {errors['state.json']}", flush=True)

    if errors:
        print("HARD ERROR: scanner selesai dengan error; workflow harus merah.", flush=True)
        for inst, error in errors.items():
            print(f"ERROR SUMMARY {inst}: {error}", flush=True)
        raise SystemExit(1)
    print("R191 scanner selesai: kedua indeks terproses.", flush=True)


if __name__ == "__main__":
    main()
