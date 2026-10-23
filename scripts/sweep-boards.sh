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
# Добавляем через GraphQL по id доски: gh project item-add требует ещё scope read:org.
jq -r 'to_entries[] | .key as $b | .value | .id as $id
  | (if .org then "\($b)\t\($id)\t\(([("org:" + .org)] + [.exclude[]? | "-repo:" + .]) | join(" "))" else empty end),
    (if (.repos // []) != [] then "\($b)\t\($id)\t\([.repos[] | "repo:" + .] | join(" "))" else empty end)' \
  "$dir/boards.json" | while IFS=$'\t' read -r board id scope; do
  gh api -X GET search/issues -f q="$scope $base" -f per_page=100 -q '.items[] | "\(.node_id) \(.html_url)"' | while read -r node url; do
    gh api graphql -f query='mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}' \
      -f p="$id" -f c="$node" >/dev/null && echo "+ $url → $board"
  done
done
