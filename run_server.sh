#!/usr/bin/env bash
set -euo pipefail

HOST="${JEKYLL_HOST:-127.0.0.1}"
PORT="${JEKYLL_PORT:-4000}"

exec bundle exec jekyll serve --host "$HOST" --port "$PORT" "$@"
