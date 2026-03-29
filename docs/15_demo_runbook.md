# KidsChef Demo Runbook

## Purpose

Use this runbook to start the local KidsChef demo, verify the core flow, and recover cleanly if the backend or AI path is unavailable.

## Local Startup

1. Start the backend from the repo root:

```bash
python3 server.py
```

2. Open the app in a browser:

```text
http://127.0.0.1:8000
```

3. For iPhone Safari on the local network, bind to all interfaces:

```bash
python3 server.py --host 0.0.0.0 --port 8000
```

## Demo Verification

Before the demo starts, verify:

- `GET /api/health` returns OK
- `GET /api/bootstrap` returns recipes and the current safety mode
- the browser shell loads `web/index.html`
- the child flow can reach meal selection, ingredients, filters, suggestions, recipe detail, and the stepper

If the backend is not healthy, do not start the demo until the basic endpoints respond.

## Demo Flow To Verify

1. Meal selection works on a phone-sized viewport.
2. Ingredient entry accepts and removes items.
3. Filters apply without hidden safety changes.
4. Suggestions show safe recipes, blocked cases, or unavailable state clearly.
5. Recipe detail shows ingredients, steps, and safety markers.
6. The stepper supports next, back, repeat, and timer behavior.
7. Favorites can be toggled and remain visible.

## Blocked Safety Case

Use one intentionally unsafe recipe or fixture to prove the safety gate:

- choose a recipe that requires a stove, oven, or knife step
- confirm the app blocks it in the active safety mode
- confirm the blocked state explains why the recipe is unavailable
- confirm the user is redirected to a safe alternative or back to filters

The blocked case must be obvious, not subtle.

## Fallback Handling

### If The Backend Is Unavailable

- stop the server
- confirm the shell shows an unavailable or degraded state
- confirm cached content or demo content does not pretend to be live
- restart `python3 server.py`
- confirm the app recovers without losing obvious UI state

### If Ollama Or The Local AI Bridge Is Unavailable

- continue the demo with curated or deterministic recipe data
- confirm the app labels AI-driven suggestions as unavailable or falls back safely
- do not block the whole demo if safe curated recipes still exist
- if a local AI bridge is later wired in this repo, stop it and repeat the fallback check

### If The Browser Loses The Local Host

- confirm the UI enters a clear degraded state
- confirm live suggestions and writes are not shown as successful
- reconnect and verify the child flow resumes cleanly

## What To Capture From The Demo

Record the following observations:

- where the user hesitated
- whether the meal selection was obvious
- whether ingredient entry was understandable
- whether filters felt too technical
- whether suggestions explained themselves
- whether safety warnings were seen before risky steps
- whether the timer was easy to notice and recover
- whether favorites felt calm and lightweight
- whether the blocked case made sense
- whether the app recovered cleanly after a backend or AI failure

## Exit Criteria

The demo is ready to proceed only when:

- the backend starts locally
- the browser reaches the full child flow
- one blocked safety case is demonstrated
- one unavailable/fallback case is demonstrated
- observations are captured immediately after the walkthrough

