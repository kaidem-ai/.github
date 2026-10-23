#!/bin/bash
# Приводит метки репозитория к labels.json: создаёт и обновляет наши, удаляет стандартные метки GitHub.
# Чужие метки (не из labels.json и не стандартные) не трогает.
# usage: scripts/sync-labels.sh <owner/repo> [extra-labels.json]
set -euo pipefail
repo=$1
dir=$(cd "$(dirname "$0")/.." && pwd)
files=("$dir/labels.json"); [ $# -ge 2 ] && files+=("$2")
for f in "${files[@]}"; do
  jq -c '.[]' "$f" | while read -r l; do
    gh label create "$(jq -r .name <<<"$l")" -R "$repo" --force \
      --color "$(jq -r .color <<<"$l")" --description "$(jq -r .description <<<"$l")" >/dev/null
  done
done
for d in documentation duplicate enhancement "good first issue" "help wanted" invalid question wontfix; do
  gh label delete "$d" -R "$repo" --yes >/dev/null 2>&1 || true
done
gh label list -R "$repo" --limit 100 | cut -f1 | tr '\n' ' '; echo
