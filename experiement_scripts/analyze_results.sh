#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_ROOT="$SCRIPT_DIR/../results/experiments"
MERGE_SCRIPT="$SCRIPT_DIR/merge_and_group_csv.py"
NORMALIZE_SCRIPT="$SCRIPT_DIR/normalizeResults.py"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      if [[ $# -lt 2 ]]; then
        echo "Usage: $0 [--path results/experiments]" >&2
        exit 1
      fi
      RESULTS_ROOT="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 [--path results/experiments]" >&2
      exit 1
      ;;
  esac
done


# DENSITY
python3 "$MERGE_SCRIPT" \
  --path="$RESULTS_ROOT/density" \
  --parameter="density" \
  --no-bucket \
  --parameter-source=description

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/density" \
  --data-folder=by_density \
  --parameter=density \
  --label=non-filtered \
  --comparison-source=filename

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/density" \
  --data-folder=by_density \
  --parameter=density \
  --filter-multiple-pne \
  --label=filtered \
  --comparison-source=filename


# MAGNITUDE
python3 "$MERGE_SCRIPT" \
  --path="$RESULTS_ROOT/magnitude" \
  --parameter="magnitude" \
  --no-bucket \
  --parameter-source=description

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/magnitude" \
  --data-folder=by_magnitude \
  --parameter=magnitude \
  --label=non-filtered \
  --comparison-source=filename

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/magnitude" \
  --data-folder=by_magnitude \
  --parameter=magnitude \
  --filter-multiple-pne \
  --label=filtered \
  --comparison-source=filename


# PATH LENGTH

python3 "$MERGE_SCRIPT" \
  --path="$RESULTS_ROOT/length" \
  --parameter="MIN SIP" \
  --parameter-source=column \
  --group_range=50 \
  --bucket-mode=zero-based \
  --add-sip-columns

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/length" \
  --data-folder="by_MIN SIP(50)" \
  --parameter="path length" \
  --comparison-source=filename \
  --label=non-filtered

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/length" \
  --data-folder="by_MIN SIP(50)" \
  --parameter="path length" \
  --comparison-source=filename \
  --filter-multiple-pne \
  --label=filtered


# SPD
python3 "$MERGE_SCRIPT" \
  --path="$RESULTS_ROOT/seperation" \
  --parameter=path_time_div \
  --parameter-source=column \
  --bucket-mode=one-based \
  --group_range=10

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/seperation" \
  --data-folder="by_path_time_div(10)" \
  --parameter=spd \
  --comparison-source=filename \
  --label=non-filtered

python3 "$NORMALIZE_SCRIPT" \
  --path="$RESULTS_ROOT/seperation" \
  --data-folder="by_path_time_div(10)" \
  --parameter=spd \
  --comparison-source=filename \
  --filter-multiple-pne \
  --label=filtered
