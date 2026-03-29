#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT/var/server.pid"
PORT="${1:-8000}"

port_listener_pid() {
  lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | head -n 1 || true
}

looks_like_kidschef_server() {
  local pid="$1"
  local command
  command="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  [[ "$command" == *"python3"* && "$command" == *"server.py"* ]]
}

if [[ ! -f "$PID_FILE" ]]; then
  PORT_PID="$(port_listener_pid)"
  if [[ -n "$PORT_PID" ]] && looks_like_kidschef_server "$PORT_PID"; then
    kill "$PORT_PID"
    echo "Stopped KidsChef server PID $PORT_PID on port $PORT"
    exit 0
  fi
  if [[ -n "$PORT_PID" ]]; then
    echo "Port $PORT is in use by PID $PORT_PID, but it does not look like KidsChef"
    exit 1
  fi
  PID="$(ps aux | awk '/python3 server.py/ && !/awk/ {print $2}' | head -n 1)"
  if [[ -z "$PID" ]]; then
    echo "No PID file found and no running KidsChef server detected"
    exit 0
  fi
  kill "$PID"
  echo "Stopped KidsChef server PID $PID"
  exit 0
fi

PID="$(cat "$PID_FILE" 2>/dev/null || true)"
if [[ -z "$PID" ]]; then
  rm -f "$PID_FILE"
  echo "PID file was empty"
  exit 0
fi

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Stopped KidsChef server PID $PID"
else
  echo "Process $PID was not running"
  FALLBACK_PID="$(ps aux | awk '/python3 server.py/ && !/awk/ {print $2}' | head -n 1)"
  if [[ -n "$FALLBACK_PID" ]]; then
    kill "$FALLBACK_PID"
    echo "Stopped detected KidsChef server PID $FALLBACK_PID"
  fi
fi

PORT_PID="$(port_listener_pid)"
if [[ -n "$PORT_PID" ]] && looks_like_kidschef_server "$PORT_PID"; then
  kill "$PORT_PID"
  echo "Stopped KidsChef server PID $PORT_PID on port $PORT"
elif [[ -n "$PORT_PID" ]]; then
  echo "Port $PORT is still in use by PID $PORT_PID, but it does not look like KidsChef"
  exit 1
fi

rm -f "$PID_FILE"
