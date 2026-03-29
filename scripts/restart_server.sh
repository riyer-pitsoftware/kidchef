#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${1:-127.0.0.1}"
PORT="${2:-8000}"

"$ROOT/scripts/stop_server.sh" "$PORT"
"$ROOT/scripts/start_server.sh" "$HOST" "$PORT"
