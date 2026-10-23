#!/bin/bash
# Настройка нового репозитория (то, что не копируется из kaidem-project-template):
# только squash-merge, коммит = заголовок и описание PR, удаление веток после merge, метки.
# Репозиторий ещё нужно добавить в boards.json и, если он в kaidem-ai, привязать к доске.
# usage: scripts/setup-repo.sh <owner/repo>
set -euo pipefail
repo=$1
gh api -X PATCH "repos/$repo" -F allow_merge_commit=false -F allow_rebase_merge=false -F allow_squash_merge=true \
  -F delete_branch_on_merge=true -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
  -q '"\(.full_name): squash only, delete branch on merge"'
"$(dirname "$0")/sync-labels.sh" "$repo"
