#!/bin/bash
# Добавляет на доски открытые задачи, которых нет ни на одной доске (boards.json):
# все репозитории организации "org", кроме "exclude", плюс отдельные репозитории "repos" (личные).
# Нужен, потому что Auto-add на бесплатном тарифе следит только за одним репозиторием,
# а личные репозитории к доске организации не привязываются.
# Запускается по расписанию (.github/workflows/sweep-boards.yml) или руками.
# usage: scripts/sweep-boards.sh
set -euo pipefail
dir=$(cd "$(dirname "$0")/.." && pwd)
base="is:issue is:open no:project"
jq -r 'to_entries[] | .key as $b | .value
  | (if .org then "\($b)\t\(([("org:" + .org)] + [.exclude[]? | "-repo:" + .]) | join(" "))" else empty end),
    (if (.repos // []) != [] then "\($b)\t\([.repos[] | "repo:" + .] | join(" "))" else empty end)' \
  "$dir/boards.json" | while IFS=$'\t' read -r board scope; do
  owner=${board%/*}; num=${board#*/}
  gh api -X GET search/issues -f q="$scope $base" -f per_page=100 -q '.items[].html_url' | while read -r url; do
    gh project item-add "$num" --owner "$owner" --url "$url" >/dev/null && echo "+ $url → $board"
  done
done
