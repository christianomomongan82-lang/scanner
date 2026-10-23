#!/usr/bin/env bash
set -euo pipefail
python runner.py --data-dir ../../data/r323 --package-dir . --out-dir ./preflight
# Only after V2 preflight PASS may the registered outcome_runner.py be called.
