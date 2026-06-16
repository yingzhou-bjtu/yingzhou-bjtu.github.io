#!/usr/bin/env bash
# Rename GitHub account + Pages repo to yingzhou-bjtu.github.io
# Requires: gh auth with user scope (gh auth refresh -h github.com -s user)

set -euo pipefail

NEW_USER="yingzhou-bjtu"
OLD_USER="Network-Optimization"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Checking gh auth (user scope)..."
gh api user --jq '.login' >/dev/null

CURRENT="$(gh api user --jq '.login')"
if [[ "$CURRENT" != "$OLD_USER" ]]; then
  echo "Logged in as $CURRENT, expected $OLD_USER. Abort."
  exit 1
fi

echo "==> Renaming GitHub account: $OLD_USER -> $NEW_USER"
gh api user -X PATCH -f login="$NEW_USER"

echo "==> Renaming Pages repo..."
gh repo rename "${NEW_USER}.github.io" -R "${NEW_USER}/Network-Optimization.github.io" -y

echo "==> Updating git remote..."
cd "$REPO_ROOT"
git remote set-url origin "git@github.com:${NEW_USER}/${NEW_USER}.github.io.git"

echo "==> Done. Site URL: https://${NEW_USER}.github.io/"
echo "    Old URLs redirect for a while; update links in papers/CV."
