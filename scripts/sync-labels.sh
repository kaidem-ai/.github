#!/bin/bash
# Приводит метки репозитория к labels.json: создаёт и обновляет наши,
# удаляет стандартные метки GitHub, только если они не стоят ни на одной задаче или PR.
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
existing=$(gh label list -R "$repo" --limit 200 --json name -q '.[].name')
for d in documentation duplicate enhancement "good first issue" "help wanted" invalid question wontfix; do
  grep -qxF "$d" <<<"$existing" || continue
  used=$(gh api -X GET search/issues -f q="repo:$repo label:\"$d\"" -q .total_count)
  if [ "$used" = "0" ]; then gh label delete "$d" -R "$repo" --yes >/dev/null; else echo "оставлена «${d}»: стоит на $used задачах/PR"; fi
done
echo "$repo: $(gh label list -R "$repo" --limit 200 --json name -q '[.[].name]|length') меток"
