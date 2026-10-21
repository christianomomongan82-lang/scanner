#!/usr/bin/env sh
set -eu
D=research/archive
cat "$D"/R319_runner_source_b64.part* | base64 -d | gzip -dc > /tmp/r319_pullback_research.py
cat "$D"/R320_runner_source_b64_small.part* | base64 -d | gzip -dc > /tmp/r320_h4_channel_breakout.py
sha256sum /tmp/r319_pullback_research.py /tmp/r320_h4_channel_breakout.py
