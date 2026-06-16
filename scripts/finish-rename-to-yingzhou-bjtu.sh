#!/usr/bin/env bash
# Complete rename after username is changed in GitHub Settings.
# GitHub.com does NOT support account rename via API — change at:
# https://github.com/settings/admin  →  Change username  →  yingzhou-bjtu

set -euo pipefail

NEW_USER="yingzhou-bjtu"
OLD_REPO="Network-Optimization.github.io"
NEW_REPO="${NEW_USER}.github.io"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAX_WAIT=600
INTERVAL=5

echo "Waiting for GitHub username to become ${NEW_USER}..."
echo "(Change it at https://github.com/settings/admin if you have not yet.)"
elapsed=0
while (( elapsed < MAX_WAIT )); do
  login="$(gh api user --jq '.login' 2>/dev/null || true)"
  if [[ "$login" == "$NEW_USER" ]]; then
    echo "Account is now ${NEW_USER}."
    break
  fi
  sleep "$INTERVAL"
  elapsed=$((elapsed + INTERVAL))
done

if [[ "$(gh api user --jq '.login')" != "$NEW_USER" ]]; then
  echo "Timed out after ${MAX_WAIT}s. Username is still $(gh api user --jq '.login')."
  exit 1
fi

echo "==> Renaming Pages repo ${OLD_REPO} -> ${NEW_REPO}"
gh repo rename "$NEW_REPO" -R "${NEW_USER}/${OLD_REPO}" -y

echo "==> Updating git remote..."
cd "$REPO_ROOT"
git remote set-url origin "git@github.com:${NEW_USER}/${NEW_REPO}.git"

echo "==> Updating _config.yml..."
sed -i "s|Network-Optimization/Network-Optimization.github.io|${NEW_USER}/${NEW_REPO}|g" _config.yml
sed -i 's|github           : "Network-Optimization"|github           : "yingzhou-bjtu"|g' _config.yml

echo "==> Done. Site URL: https://${NEW_USER}.github.io/"
echo "    Run: git add -A && git commit && git push -u origin main"
