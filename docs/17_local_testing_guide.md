# KidsChef Local Testing Guide

Use this guide to run and test KidsChef locally before a demo or a development session.

## Prerequisites

- Python `3.11+`
- Node available locally for `node --check web/app.js`
- Repo cloned at `/Users/riyer/code/kidschef`
- Optional: Ollama running locally if you want to test the backend-only AI seam

## Configure Local Runtime With `.env`

Create a local `.env` file in the repo root.

Start from:

```bash
cp .env.example .env
```

Recommended Ollama settings:

```bash
KIDS_CHEF_OLLAMA_ENABLED=true
KIDS_CHEF_OLLAMA_HOST=http://127.0.0.1:11434
KIDS_CHEF_OLLAMA_MODEL=llama3.2:latest
KIDS_CHEF_OLLAMA_TIMEOUT_SECONDS=5
KIDS_CHEF_OLLAMA_MAX_CANDIDATES=5
```

`server.py` loads `.env` from the repo root automatically on startup.

## Start The App

From the repo root:

```bash
cd /Users/riyer/code/kidschef
./scripts/start_server.sh
```

Open:

```text
http://127.0.0.1:8000/
```

For iPhone Safari on the same local network:

```bash
cd /Users/riyer/code/kidschef
./scripts/start_server.sh 0.0.0.0 8000
```

Then open the machine's local network IP on the phone, for example:

```text
http://192.168.x.x:8000/
```

## Restart The App

1. Stop the running `python3 server.py` process.
2. Restart with:
   ```bash
   cd /Users/riyer/code/kidschef
   ./scripts/restart_server.sh
   ```
3. For LAN mode:
   ```bash
   cd /Users/riyer/code/kidschef
   ./scripts/restart_server.sh 0.0.0.0 8000
   ```
3. Re-run the quick checks below before continuing.

## Tail The Log

The server log lives at:

```text
/Users/riyer/code/kidschef/var/server.log
```

Tail it with:

```bash
cd /Users/riyer/code/kidschef
./scripts/tail_server_log.sh
```

This log now includes the outbound request sent to Ollama and the returned response or failure.

## Quick API Checks

Health:

```bash
curl -s http://127.0.0.1:8000/api/health
```

Bootstrap:

```bash
curl -s http://127.0.0.1:8000/api/bootstrap
```

Recommendation request:

```bash
curl -s -X POST http://127.0.0.1:8000/api/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"mealType":"breakfast","ingredients":["plain yogurt"],"filters":{"allergens":[],"diets":[],"appliances":["microwave"]},"safetyMode":"standard"}'
```

Expected:

- health returns `{"ok": true, ...}`
- bootstrap returns recipes, favorites, and `safetyMode`
- recommendations return safe recipe records

## Static Verification

Run these from the repo root:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q kidschef kidschef_backend tests server.py
node --check web/app.js
```

## Demo-Focused Browser Checks

In the browser, verify:

1. Meal selection loads immediately.
2. Ingredient chips can be added and removed.
3. Filters can be toggled without breaking the flow.
4. Suggestion review shows safe results clearly.
5. Recipe detail shows ingredients, steps, and safety markers.
6. The stepper supports `next`, `back`, `repeat`, and timer behavior.
7. Favorites toggle and persist.
8. A blocked safety case is visible and understandable.

## Optional Ollama Testing

Ollama is backend-only and disabled by default unless enabled in `.env`.

After editing `.env`, restart the server and repeat the recommendation check.

Expected:

- the backend still returns safe recommendations
- `ai_assistance` appears in the recommendation response
- if Ollama is unavailable, the backend falls back safely instead of failing the entire request

## If Something Fails

- If the backend does not start, fix that before opening the browser.
- If the browser loads but API calls fail, verify `/api/health` and `/api/bootstrap` first.
- If Ollama is unavailable, leave it disabled and continue with deterministic mode.
- For the live demo flow, use:
  - [15_demo_runbook.md](/Users/riyer/code/kidschef/docs/15_demo_runbook.md)
  - [16_demo_facilitator_script.md](/Users/riyer/code/kidschef/docs/16_demo_facilitator_script.md)
