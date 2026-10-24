#!/usr/bin/env bash
set -euo pipefail
INST="$1"
YEAR="$2"
OUT="$3"
mkdir -p dl/chunks
NEXT=$((YEAR + 1))
# Dukascopy returned empty files before this instrument's source-history start.
# Keep US Small Cap 2000 in every pooled test from its first available M5 bar onward.
HISTORY_START="2017-01-01"
if [ "$INST" = "ussc2000idxusd" ]; then HISTORY_START="2018-08-08"; fi

for Q in 1 2 3 4; do
  case "$Q" in
    1) QM=01; QTO="$YEAR-04-01" ;;
    2) QM=04; QTO="$YEAR-07-01" ;;
    3) QM=07; QTO="$YEAR-10-01" ;;
    4) QM=10; if [ "$YEAR" -eq 2026 ]; then QTO="now"; else QTO="$NEXT-01-01"; fi ;;
  esac

  QB="$INST"_m5q_"$YEAR"_Q"$Q"
  QC="dl/chunks/$QB.csv.gz"
  QR="dl/chunks/$QB.csv"
  if [ -s "$QC" ] && gzip -t "$QC" >/dev/null 2>&1; then
    echo "QUARTER CACHE HIT: $QB"
    continue
  fi

  FROM="$YEAR-$QM-01"
  if [ "$QTO" != "now" ] && { [[ "$QTO" < "$HISTORY_START" ]] || [[ "$QTO" == "$HISTORY_START" ]]; }; then
    echo "NO SOURCE HISTORY: $QB ends before $HISTORY_START; quarter is absent by source availability, not removed from the basket."
    continue
  fi
  MAX_ATTEMPTS=4
  OK=false
  for ATTEMPT in $(seq 1 "$MAX_ATTEMPTS"); do
    rm -f "$QR" "$QC"
    echo "DOWNLOAD $QB: $FROM to $QTO (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    echo "BOUNDED REQUEST: timeout=180s; attempt=$ATTEMPT/$MAX_ATTEMPTS"
    if timeout 180s npx --yes dukascopy-node@1.50.0 \
      -i "$INST" -from "$FROM" -to "$QTO" \
      -t m5 -p bid -utc 0 -f csv -fl \
      -dir dl/chunks -fn "$QB" \
      -bs 10 -bp 1000 -r 5 -rp 1000; then
      LINES=$(wc -l < "$QR" 2>/dev/null || echo 0)
      if [ -s "$QR" ] && [ "$LINES" -gt 1000 ] && gzip -1 "$QR" && gzip -t "$QC"; then
        echo "SAVED $QC ($(du -h "$QC" | cut -f1), rows=$((LINES - 1)))"
        OK=true
        break
      fi
    fi
    rm -f "$QR"
    if [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; then sleep $((ATTEMPT * 20)); fi
  done
  if [ "$OK" != "true" ]; then
    echo "ERROR: quarterly M5 download failed: $QB" >&2
    exit 1
  fi
done

RAW="dl/chunks/$INST"_"m5"_"$YEAR".csv
rm -f "$RAW" "$OUT"
FIRST=true
for Q in 1 2 3 4; do
  QB="$INST"_m5q_"$YEAR"_Q"$Q"
  QC="dl/chunks/$QB.csv.gz"
  if [ ! -s "$QC" ] || ! gzip -t "$QC" >/dev/null 2>&1; then
    echo "SKIP ABSENT PRE-INCEPTION QUARTER: $QB"
    continue
  fi
  if [ "$FIRST" = "true" ]; then
    gzip -cd "$QC" > "$RAW"
    FIRST=false
  else
    gzip -cd "$QC" | tail -n +2 >> "$RAW"
  fi
done
if [ "$FIRST" = "true" ]; then
  rm -f "$RAW" "$OUT"
  echo "NO SOURCE DATA for $INST in $YEAR before its documented history start $HISTORY_START."
  exit 0
fi
LINES=$(wc -l < "$RAW" 2>/dev/null || echo 0)
if [ ! -s "$RAW" ] || [ "$LINES" -le 1000 ] || ! gzip -1 "$RAW" || ! gzip -t "$OUT"; then
  rm -f "$RAW" "$OUT"
  echo "ERROR: failed to join M5 quarterly chunks into $OUT" >&2
  exit 1
fi
echo "SAVED ANNUAL M5 CHUNK: $OUT ($(du -h "$OUT" | cut -f1), rows=$((LINES - 1)))"
