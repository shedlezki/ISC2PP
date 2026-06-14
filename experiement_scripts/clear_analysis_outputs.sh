#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_ROOT="$SCRIPT_DIR/../results/experiments"

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

remove_path() {
  local path="$1"
  if [[ -e "$path" || -d "$path" ]]; then
    rm -rf "$path"
    echo "Removed $path"
  fi
}

remove_glob_paths() {
  local pattern="$1"
  shopt -s nullglob
  local IFS=$'\n'
  local match
  for match in $pattern; do
    remove_path "$match"
  done
  shopt -u nullglob
}

clear_normalize_outputs() {
  local root="$1"

  remove_glob_paths "$root/filtered*"
  remove_glob_paths "$root/non-filtered*"
  remove_glob_paths "$root/by_*"
  remove_path "$root/merged_data.csv"
}

clear_normalize_outputs "$RESULTS_ROOT/density"
clear_normalize_outputs "$RESULTS_ROOT/magnitude"
clear_normalize_outputs "$RESULTS_ROOT/length"
clear_normalize_outputs "$RESULTS_ROOT/seperation"
