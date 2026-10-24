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
    if timeout 120s npx --yes dukascopy-node@1.50.0 \
      -i "$INST" -from "$start" -to "$end" \
      -t m5 -p bid -utc 0 -f csv -fl \
      -dir dl/chunks -fn "$name" \
      -bs 10 -bp 1000 -r 3 -rp 1500; then
      lines=$(wc -l < "$raw" 2>/dev/null || echo 0)
      if [ -s "$raw" ] && [ "$lines" -ge "$min_lines" ] && gzip -1 "$raw" && gzip -t "$gz"; then
        echo "RANGE SAVED $gz ($((lines - 1)) rows)"
        return 0
      fi
    fi
    rm -f "$raw" "$gz"
    if [ "$attempt" -lt 2 ]; then sleep 10; fi
  done

  start_s=$(date -u -d "$start" +%s)
  end_s=$(date -u -d "$end" +%s)
  days=$(( (end_s - start_s) / 86400 ))
  if [ "$days" -le 1 ]; then
    echo "ERROR: irreducible one-day source range failed: $name ($start to $end)" >&2
    return 1
  fi

  half=$((days / 2))
  mid=$(date -u -d "$start + $half days" +%F)
  if [ "$mid" = "$start" ] || [ "$mid" = "$end" ]; then
    echo "ERROR: could not split date interval safely: $name ($start to $end)" >&2
    return 1
  fi
  left_name="${name}_partA_${start//-/}"
  right_name="${name}_partB_${mid//-/}"
  left_gz="dl/chunks/${left_name}.csv.gz"
  right_gz="dl/chunks/${right_name}.csv.gz"

  if ! fetch_range "$start" "$mid" "$left_name" 1; then return 1; fi
  if ! fetch_range "$mid" "$end" "$right_name" 1; then return 1; fi

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
