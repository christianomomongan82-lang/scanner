import os, subprocess, datetime, time
import numpy as np, pandas as pd, requests

INST = {"usa500idxusd": "S&P 500", "usatechidxusd": "Nasdaq 100"}
N, M, RR = 55, 27, 2.0


def to_h4(h1):
    h1 = h1.copy()
    h1.index = h1.index.tz_convert("America/New_York")
    return h1.resample("4h", offset="1h", label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def check(h4, now_utc):
    h = h4[h4.index.tz_convert("UTC") + pd.Timedelta(hours=4) <= now_utc]
    if len(h) < N + 2:
        return None
    c, hi, lo = h.close.values, h.high.values, h.low.values
    i = len(h) - 1
    close_time = h.index[i].tz_convert("UTC") + pd.Timedelta(hours=4)
    if not (c[i] > hi[i - N:i].max()):
        return None
    sl = lo[i - M + 1:i + 1].min()
    risk = c[i] - sl
    if risk <= 0:
        return None
    return dict(close_time=close_time, entry=c[i], sl=sl, tp=c[i] + RR * risk, risk_pct=100 * risk / c[i])


def fetch(inst):
    today = datetime.date.today()
    frm = today - datetime.timedelta(days=45)
    outdir = "dl"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, inst + ".csv")

    # Dukascopy sometimes returns HTTP 202 instead of a completed data response.
    # Lower request concurrency and retry both at the downloader and whole-command level.
    cmd = [
        "npx", "--yes", "dukascopy-node",
        "-i", inst, "-from", str(frm), "-to", "now",
        "-t", "h1", "-p", "bid", "-f", "csv",
        "-fl", "-dir", outdir, "-fn", inst,
        "-bs", "3", "-bp", "2000",
        "-r", "5", "-re", "-rp", "5000"
    ]

    last_error = "Unknown download error"
    for attempt in range(1, 4):
        if os.path.exists(path):
            os.remove(path)

        # JETTA currently returns HTTP 202 with an empty body unless the
        # request includes the official Dukascopy Origin and Referer headers.
        node_env = os.environ.copy()
        patch_path = os.path.abspath("dukascopy_fetch_patch.cjs")
        preload = f"--require={patch_path}"
        existing_options = node_env.get("NODE_OPTIONS", "").strip()
        node_env["NODE_OPTIONS"] = f"{existing_options} {preload}".strip()

        result = subprocess.run(
            cmd, check=False, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, env=node_env
        )
        output = result.stdout or ""
        if output:
            print(output, end="" if output.endswith("\n") else "\n", flush=True)

        if result.returncode != 0:
            last_error = f"Dukascopy CLI exit code {result.returncode}"
        elif not os.path.isfile(path):
            last_error = f"Dukascopy tidak membuat file CSV: {path}"
        elif os.path.getsize(path) == 0:
            last_error = f"Dukascopy membuat CSV kosong: {path}"
        else:
            try:
                d = pd.read_csv(path)
                required = {"timestamp", "open", "high", "low", "close"}
                missing = required.difference(d.columns)
                if d.empty:
                    raise ValueError("CSV hanya berisi header, tanpa bar data")
                if missing:
                    raise ValueError(f"Kolom wajib hilang: {sorted(missing)}")

                ts = d["timestamp"]
                index = (
                    pd.to_datetime(ts, unit="ms", utc=True)
                    if np.issubdtype(ts.dtype, np.number)
                    else pd.to_datetime(ts, utc=True)
                )
                bars = d[["open", "high", "low", "close"]].astype(float)
                bars.index = index
                if bars.empty:
                    raise ValueError("CSV tidak menghasilkan bar OHLC")
                return bars
            except Exception as exc:
                last_error = f"CSV Dukascopy tidak valid: {type(exc).__name__}: {exc}"

        if attempt < 3:
            wait_seconds = 10 * attempt
            print(
                f"Download {inst} gagal (percobaan {attempt}/3: {last_error}). "
                f"Mencoba ulang dalam {wait_seconds} detik.",
                flush=True
            )
            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Gagal mengunduh data Dukascopy untuk {inst} setelah 3 percobaan. "
        f"Kesalahan terakhir: {last_error}"
    )


def notify(title, msg):
    repo = os.environ["GITHUB_REPOSITORY"]
    requests.post("https://api.github.com/repos/" + repo + "/issues", headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"], "Accept": "application/vnd.github+json"}, json={"title": title, "body": "@" + os.environ["GITHUB_REPOSITORY_OWNER"] + "\n\n" + msg}, timeout=20)


def main():
    now = pd.Timestamp.now(tz="UTC")
    manual = os.environ.get("EVENT") == "workflow_dispatch"
    notify("Scanner aktif (tes)", "Tes berhasil. Sinyal akan muncul sebagai issue baru dan masuk ke email lo.") if manual else None
    for inst, name in INST.items():
        s = check(to_h4(fetch(inst)), now)
        fresh = s is not None and (now - s["close_time"]) <= pd.Timedelta(minutes=65)
        notify("SINYAL BUY " + name, "Entry sekarang ~%.1f\nSL %.1f\nTP %.1f\nRisiko %.2f%% dari harga\nSkip kalau sudah punya posisi di indeks ini." % (s["entry"], s["sl"], s["tp"], s["risk_pct"])) if fresh else None


main() if __name__ == "__main__" else None
