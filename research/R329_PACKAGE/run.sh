#!/usr/bin/env bash
set -euo pipefail
python runner.py --data-dir ../../data/r323 --package-dir . --out-dir .
python ../../research/verify_experiment_package_v2.py preflight .
