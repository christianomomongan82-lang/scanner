#!/usr/bin/env sh
set -eu
D=research/archive
cat "$D"/R319_runner_source_b64.part* | base64 -d | gzip -dc > /tmp/r319_pullback_research.py
cat "$D"/R320_runner_source_b64_small.part* | base64 -d | gzip -dc > /tmp/r320_h4_channel_breakout.py
# Use deterministic gzip headers so ledger bytes and hashes stay identical across reruns.
python - <<'PY'
from pathlib import Path
for name in ("/tmp/r319_pullback_research.py", "/tmp/r320_h4_channel_breakout.py"):
    p = Path(name)
    src = p.read_text()
    old = "index=False,compression='gzip')"
    new = "index=False,compression={'method':'gzip','mtime':0})"
    if old not in src:
        if new not in src:
            raise SystemExit(f"Expected output compression statement not found in {name}")
    else:
        src = src.replace(old, new)
        p.write_text(src)
PY
sha256sum /tmp/r319_pullback_research.py /tmp/r320_h4_channel_breakout.py
