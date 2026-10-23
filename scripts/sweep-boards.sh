#!/bin/bash
# Добавляет на доски открытые задачи из их репозиториев, которых нет ни на одной доске (boards.json).
# Нужен, потому что Auto-add на бесплатном тарифе следит только за одним репозиторием,
# а личные репозитории к доске организации не привязываются. Позже это делает agent-pm.
# usage: scripts/sweep-boards.sh
set -euo pipefail
dir=$(cd "$(dirname "$0")/.." && pwd)
jq -r 'to_entries[] | .key as $b | .value.repos[] | "\($b) \(.)"' "$dir/boards.json" | while read -r board repo; do
  owner=${board%/*}; num=${board#*/}
  gh api -X GET search/issues -f q="repo:$repo is:issue is:open no:project" -q '.items[].html_url' | while read -r url; do
    gh project item-add "$num" --owner "$owner" --url "$url" >/dev/null && echo "+ $url → $board"
  done
done
