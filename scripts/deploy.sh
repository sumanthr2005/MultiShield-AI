#!/usr/bin/env sh
set -eu

APP_DIR=${APP_DIR:-/opt/multishield-ai}

cd "$APP_DIR"

if [ -d .git ]; then
  git fetch --all --prune
  git reset --hard origin/main
fi

docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build --remove-orphans

docker compose -f docker-compose.yml -f docker-compose.monitoring.yml ps