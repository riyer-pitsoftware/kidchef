#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/var"
LOG_FILE="$LOG_DIR/server.log"
PID_FILE="$LOG_DIR/server.pid"
HOST="${1:-127.0.0.1}"
PORT="${2:-8000}"

mkdir -p "$LOG_DIR"

port_listener_pid() {
  lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | head -n 1 || true
}

looks_like_kidschef_server() {
  local pid="$1"
  local command
  command="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  [[ "$command" == *"python3"* && "$command" == *"server.py"* ]]
}

EXISTING_PID=""
if [[ -f "$PID_FILE" ]]; then
  EXISTING_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "${EXISTING_PID}" ]] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "KidsChef server already running with PID $EXISTING_PID"
    echo "Log: $LOG_FILE"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

EXISTING_PID="$(ps aux | awk '/python3 server.py/ && !/awk/ {print $2}' | head -n 1)"
if [[ -n "${EXISTING_PID}" ]]; then
  echo "KidsChef server already running with PID $EXISTING_PID"
  echo "Use ./scripts/restart_server.sh to replace it cleanly."
  echo "Log: $LOG_FILE"
  exit 0
fi

PORT_PID="$(port_listener_pid)"
if [[ -n "${PORT_PID}" ]]; then
  if looks_like_kidschef_server "$PORT_PID"; then
    echo "KidsChef server is already listening on port $PORT with PID $PORT_PID"
    echo "Use ./scripts/restart_server.sh to replace it cleanly."
  else
    echo "Port $PORT is already in use by PID $PORT_PID"
    echo "Refusing to start KidsChef over another process."
  fi
  echo "Log: $LOG_FILE"
  exit 1
fi

cd "$ROOT"
nohup env PYTHONUNBUFFERED=1 python3 server.py --host "$HOST" --port "$PORT" </dev/null >>"$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" >"$PID_FILE"
sleep 1
if ! kill -0 "$PID" 2>/dev/null; then
  echo "KidsChef server failed to stay running"
  echo "Log: $LOG_FILE"
  rm -f "$PID_FILE"
  tail -n 40 "$LOG_FILE" 2>/dev/null || true
  exit 1
fi
echo "Started KidsChef server"
echo "PID: $PID"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Log: $LOG_FILE"
