#!/usr/bin/env bash
# Recover an otherwise unavailable M5 BID range by recursively splitting it.
# No price bars are invented or silently skipped: if a final one-day request fails,
# the interval remains a hard failure. Successful partial ranges are cached as gzip.
set -euo pipefail
INST="$1"
FROM="$2"
TO="$3"
BASE="$4"
mkdir -p dl/chunks

fetch_range() {
  local start="$1" end="$2" name="$3" min_lines="$4"
  local raw="dl/chunks/${name}.csv" gz="dl/chunks/${name}.csv.gz"
  local lines attempt start_s end_s days half mid left_name right_name left_gz right_gz

  if [ -s "$gz" ] && gzip -t "$gz" >/dev/null 2>&1; then
    lines=$(gzip -cd "$gz" 2>/dev/null | wc -l || echo 0)
    if [ "$lines" -ge "$min_lines" ]; then
      echo "RANGE CACHE HIT: $name ($lines lines)"
      return 0
    fi
  fi

  # Current/future periods are optional in the parent workflow; do not recurse
  # across an open-ended or not-yet-started range.
  if [ "$end" = "now" ]; then
    echo "OPEN-ENDED RANGE NOT SPLIT: $name"
    return 1
  fi
  local today
  today=$(date -u +%F)
  if [[ "$start" > "$today" ]]; then
    echo "FUTURE RANGE NOT FETCHED: $name ($start)"
    return 1
  fi

  for attempt in 1 2; do
    rm -f "$raw" "$gz"
    echo "RANGE REQUEST $name: $start to $end (attempt $attempt/2; timeout 120s)"
    if timeout --kill-after=10s 120s npx --yes dukascopy-node@1.50.0 \
      -i "$INST" -from "$start" -to "$end" \
      -t m5 -p bid -utc 0 -f csv -fl \
      -dir dl/chunks -fn "$name" \
      -bs 10 -bp 1000 -r 5 -rp 5000; then
      lines=$(wc -l < "$raw" 2>/dev/null || echo 0)
      if [ -s "$raw" ] && [ "$lines" -ge "$min_lines" ] && gzip -1 "$raw" && gzip -t "$gz"; then
        echo "RANGE SAVED $gz ($((lines - 1)) rows)"
        return 0
      fi
    fi
    rm -f "$raw" "$gz"
    if [ "$attempt" -lt 2 ]; then sleep 15; fi
  done

  start_s=$(date -u -d "$start" +%s)
  end_s=$(date -u -d "$end" +%s)
  seconds=$(( end_s - start_s ))
  if [ "$seconds" -le 86400 ]; then
    # The provider sometimes returns HTTP 503 for a wider request even though
    # smaller batches succeed. Try the one-day (or shorter) leaf with batch-size
    # one and longer retries before declaring this source interval unavailable.
    for attempt in 1 2 3 4 5; do
      rm -f "$raw" "$gz"
      echo "NARROW-RANGE RECOVERY $name: $start to $end (attempt $attempt/5; batch-size=1)"
      if timeout --kill-after=10s 120s npx --yes dukascopy-node@1.50.0 \
        -i "$INST" -from "$start" -to "$end" \
        -t m5 -p bid -utc 0 -f csv -fl \
        -dir dl/chunks -fn "$name" \
        -bs 1 -bp 1000 -r 15 -rp 5000; then
        lines=$(wc -l < "$raw" 2>/dev/null || echo 0)
        if [ -s "$raw" ] && [ "$lines" -ge "$min_lines" ] && gzip -1 "$raw" && gzip -t "$gz"; then
          echo "NARROW-RANGE SAVED $gz ($((lines - 1)) rows)"
          return 0
        fi
      fi
      rm -f "$raw" "$gz"
      if [ "$attempt" -lt 5 ]; then sleep $((attempt * 15)); fi
    done
    # Last resort: use the official Dukascopy Jetta BID M1 API and aggregate only
    # complete M1 groups to M5. The Python helper checks same-instrument native-M5
    # equivalence first; if it cannot prove equivalence, this source gap stays fatal.
    rm -f "$raw" "$gz"
    echo "NATIVE M5 FAILED: attempting same-source Jetta M1->M5 recovery for $name ($start to $end)"
    if python research/recover_m5_by_jettam1.py --instrument "$INST" --start "$start" --end "$end" --output "$raw"; then
      lines=$(wc -l < "$raw" 2>/dev/null || echo 0)
      if [ -s "$raw" ] && [ "$lines" -ge "$min_lines" ] && gzip -1 "$raw" && gzip -t "$gz"; then
        echo "Jetta M1->M5 source-recovery saved $gz ($((lines - 1)) rows)"
        return 0
      fi
    fi
    rm -f "$raw" "$gz"
    echo "ERROR: irreducible source interval failed after native and same-source recovery attempts: $name ($start to $end)" >&2
    return 1
  fi

  if [ "$seconds" -lt 0 ]; then
    echo "ERROR: invalid reversed date interval: $name ($start to $end)" >&2
    return 1
  fi
  half=$((seconds / 2))
  mid=$(date -u -d "@$((start_s + half))" +%F)
  if [ "$mid" = "$start" ] || [ "$mid" = "$end" ]; then
    echo "ERROR: could not split date interval safely: $name ($start to $end)" >&2
    return 1
  fi
  left_name="${name}_partA_${start//-/}"
  right_name="${name}_partB_${mid//-/}"
  left_gz="dl/chunks/${left_name}.csv.gz"
  right_gz="dl/chunks/${right_name}.csv.gz"

  # Try both child intervals even if one fails. This retains successful source
  # ranges in the cache, making the next retry resume instead of redownloading
  # the already recovered half. A failed leaf still makes the overall range fail.
  LEFT_OK=true
  RIGHT_OK=true
  if ! fetch_range "$start" "$mid" "$left_name" 1; then LEFT_OK=false; fi
  if ! fetch_range "$mid" "$end" "$right_name" 1; then RIGHT_OK=false; fi
  if [ "$LEFT_OK" != "true" ] || [ "$RIGHT_OK" != "true" ]; then
    echo "ERROR: split range incomplete; successful child segments retained: $name" >&2
    return 1
  fi

  rm -f "$raw" "$gz"
  gzip -cd "$left_gz" > "$raw"
  gzip -cd "$right_gz" | tail -n +2 >> "$raw"
  lines=$(wc -l < "$raw" 2>/dev/null || echo 0)
  if [ "$lines" -lt "$min_lines" ]; then
    rm -f "$raw"
    echo "ERROR: split ranges combined below minimum coverage: $name lines=$lines required=$min_lines" >&2
    return 1
  fi
  if ! gzip -1 "$raw" || ! gzip -t "$gz"; then
    rm -f "$raw" "$gz"
    echo "ERROR: could not create merged source cache for $name" >&2
    return 1
  fi
  rm -f "$left_gz" "$right_gz"
  echo "RANGE RECOVERED BY SPLITTING: $gz ($((lines - 1)) rows)"
  return 0
}

fetch_range "$FROM" "$TO" "$BASE" 201
