#!/usr/bin/env python3
"""Readable R227-R234 rule mirror. Exact local engine and full ledgers are in the ZIP."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

SYMS=["usa500idxusd","usatechidxusd","usa30idxusd","ussc2000idxusd","deuidxeur","gbridxgbp","fraidxeur","eusidxeur","ausidxaud","jpnidxjpy"]
RULES={
"R227":{"name":"multi-horizon alignment momentum","hold_hours":8,"entry":"24 observed non-flat bars return >= +/-0.40%, 4 active-bar return confirms >= +/-0.15%, current body confirms"},
"R228":{"name":"volatility-shock close-location continuation","hold_hours":4,"entry":"current range >=2x prior 24-active-bar median, 4-active-bar return >= +/-0.20%, close in outer 20%"},
"R229":{"name":"high-range wick rejection","hold_hours":4,"entry":"range >=2x prior 24-active-bar median; rejection wick >=60%, close-location confirms reversal"},
"R230":{"name":"24-active-bar extreme sweep and re-entry","hold_hours":4,"entry":"sweep previous 24-active-bar high/low and close back inside by >=0.15% with reversal body"},
"R231":{"name":"72-active-bar directional-efficiency continuation","hold_hours":12,"entry":"72 active-bar return >= +/-0.80%, efficiency >=0.45, current body confirms"},
"R232":{"name":"12-active-bar overextension reversal","hold_hours":6,"entry":"12 active-bar return magnitude >=0.80%, current body turns and close-location confirms"},
"R233":{"name":"cross-sectional 12-active-bar momentum","hold_hours":8,"entry":"at exact common times, trade top/bottom two indices in momentum direction if return >= +/-0.15%"},
"R234":{"name":"weekend carry directional drift","hold_hours":48,"entry":"Friday H1 bar at 14:00 UTC (closes 15:00), prior 24 active-bar return >= +/-0.40%"}
}
DISCOVERY=("2017-01-01T00:00:00Z","2022-01-01T00:00:00Z")
FORWARD=("2022-01-01T00:00:00Z","2026-01-01T00:00:00Z")
OOS=("2026-01-01T00:00:00Z","2026-10-10T00:00:00Z")
DISCOVERY_MIN_TRADES=100
DISCOVERY_MIN_PF_2BPS=1.0
FORWARD_MIN_TRADES=30
FORWARD_MIN_PF_1BPS=1.15
FORWARD_MIN_PF_2BPS=1.15
# Exact feature/signal implementation lives in the exact local runner embedded in r227_r234_batch_bundle.zip.
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default="/mnt/data/r205_snapshot")
    ap.add_argument("--out-dir",default="/mnt/data/r227_r234_batch_results")
    ap.add_argument("--rules-only",action="store_true",help="print the preregistered rules without running the compact mirror")
    a=ap.parse_args()
    if a.rules_only:
        for k,v in RULES.items(): print(k,v)
        return
    raise SystemExit("This branch copy is a rule mirror. For the exact runnable engine and ledger generation, use engine/r227_r234_batch.py from the ZIP.")
if __name__=="__main__": main()
