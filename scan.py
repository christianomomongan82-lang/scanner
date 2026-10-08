import os, subprocess, datetime
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
    to = today + datetime.timedelta(days=1)
    subprocess.run(["npx", "--yes", "dukascopy-node", "-i", inst, "-from", str(frm), "-to", str(to), "-t", "h1", "-p", "bid", "-f", "csv", "-fl", "-dir", "dl", "-fn", inst, "-s"], check=True)
    d = pd.read_csv("dl/" + inst + ".csv")
    ts = d["timestamp"]
    d.index = pd.to_datetime(ts, unit="ms", utc=True) if np.issubdtype(ts.dtype, np.number) else pd.to_datetime(ts, utc=True)
    return d[["open", "high", "low", "close"]].astype(float)
def notify(title, msg):
    repo = os.environ["GITHUB_REPOSITORY"]
    requests.post("https://api.github.com/repos/" + repo + "/issues", headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"], "Accept": "application/vnd.github+json"}, json={"title": title, "body": msg}, timeout=20)
def main():
    now = pd.Timestamp.now(tz="UTC")
    manual = os.environ.get("EVENT") == "workflow_dispatch"
    notify("Scanner aktif (tes)", "Tes berhasil. Sinyal akan muncul sebagai issue baru dan masuk ke email lo.") if manual else None
    for inst, name in INST.items():
        s = check(to_h4(fetch(inst)), now)
        fresh = s is not None and (now - s["close_time"]) <= pd.Timedelta(minutes=65)
        notify("SINYAL BUY " + name, "Entry sekarang ~%.1f\nSL %.1f\nTP %.1f\nRisiko %.2f%% dari harga\nSkip kalau sudah punya posisi di indeks ini." % (s["entry"], s["sl"], s["tp"], s["risk_pct"])) if fresh else None
main() if __name__ == "__main__" else None
