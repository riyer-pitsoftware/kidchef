#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$ROOT/var/server.log"

mkdir -p "$ROOT/var"
touch "$LOG_FILE"
tail -f "$LOG_FILE"
