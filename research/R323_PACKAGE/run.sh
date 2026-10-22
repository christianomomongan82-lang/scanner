#!/usr/bin/env bash
set -euo pipefail
python runner.py --audit-only --data-dir ../../data/r323 --out-dir ./audit
# Exit 1 is expected: the frozen sample gate fails before PnL.
python runner.py --data-dir ../../data/r323 --out-dir ./preoutcome
# Do not add --execute: no PnL is authorised for this failed sample.
