# KidsChef Technical README

KidsChef is a local-first mobile web MVP for ages 10-14. The current implementation is a zero-dependency Python server plus a static browser shell, backed by Ollama-generated recipes and deterministic rule validation.

## Current Structure

The repo is split into four active layers:

- `kidschef/`
  Shared recipe/filter types and deterministic safety filtering rules.
- `kidschef_backend/`
  Local backend layer. This package owns request parsing, the recipe service, the favorites store, and the HTTP server wiring.
- `web/`
  Mobile-first browser shell. This is a static frontend that talks to the local JSON API and renders the child flow.
- `docs/`
  Product, safety, platform, AI, UX, and QA contracts that drove the implementation split.

## Backend/Frontend Reconciliation

The parallel implementation drafts were reconciled around the server boundary rather than by rewriting the frontend.

The backend now does three things:

- serves `web/index.html`, `web/app.js`, and `web/styles.css`
- exposes the API shapes the shell currently expects
- generates recipe records through local Ollama and validates them before returning them to the shell

The supported local API surface is:

- `GET /`
  Serves the KidsChef web shell.
- `GET /api/health`
  Basic service health.
- `GET /api/bootstrap`
  Returns current favorites and the default safety mode for initial client boot. There is no static recipe catalog.
- `POST /api/recommendations`
  Returns filtered full recipe records for the active meal, ingredients, filters, and safety mode.
- `GET /api/recipes/<id>`
  Returns a single full recipe record.
- `POST /api/favorites/toggle`
  Toggles favorite state and returns the updated recipe plus current favorites.

Compatibility aliases are also preserved for backend-oriented callers:

- `POST /api/recipes/suggest`

## Data Flow

The local flow is:

1. The browser loads `/`.
2. `web/app.js` calls `GET /api/bootstrap`.
3. The shell sends recommendation requests to `POST /api/recommendations`.
4. The backend calls local Ollama to generate recipe options.
5. The backend converts the generated recipes into internal recipe models.
6. Deterministic validation in `kidschef.safety_filtering` enforces meal, allergen, diet, appliance, and safety-mode rules.
7. Valid generated recipes are returned to the shell as full records so the child can move directly into recipe detail and the stepper.

## Ollama Generation

Local LLM access is backend-only.

- The browser never calls Ollama directly.
- The backend uses Ollama to generate the recipe options shown in the app.
- If Ollama is disabled, unavailable, or returns unusable output, there is no static recipe fallback.

Current environment variables:

- `KIDS_CHEF_OLLAMA_ENABLED`
- `KIDS_CHEF_OLLAMA_HOST`
- `KIDS_CHEF_OLLAMA_MODEL`
- `KIDS_CHEF_OLLAMA_TIMEOUT_SECONDS`
- `KIDS_CHEF_OLLAMA_MAX_CANDIDATES`

The current seam is conservative in a different way: Ollama generates the recipes, but deterministic validation still decides whether a generated recipe can be shown.

## Key Files

- [server.py](/Users/riyer/code/kidschef/server.py)
  CLI entrypoint for the local server.
- [kidschef/recipe_models.py](/Users/riyer/code/kidschef/kidschef/recipe_models.py)
  Canonical recipe and filter dataclasses.
- [kidschef/safety_filtering.py](/Users/riyer/code/kidschef/kidschef/safety_filtering.py)
  Deterministic safety and filter logic.
- [kidschef_backend/repository.py](/Users/riyer/code/kidschef/kidschef_backend/repository.py)
  Local favorites persistence and optional in-memory seams.
- [kidschef_backend/services.py](/Users/riyer/code/kidschef/kidschef_backend/services.py)
  Service-layer orchestration between request contracts, Ollama generation, validation, and favorites.
- [kidschef_backend/app.py](/Users/riyer/code/kidschef/kidschef_backend/app.py)
  HTTP routing and static file serving.
- [web/app.js](/Users/riyer/code/kidschef/web/app.js)
  Frontend state machine and child flow rendering.
- [docs/15_demo_runbook.md](/Users/riyer/code/kidschef/docs/15_demo_runbook.md)
  Operational checklist for running the live demo.
- [docs/16_demo_facilitator_script.md](/Users/riyer/code/kidschef/docs/16_demo_facilitator_script.md)
  Child/parent walkthrough and observation prompts for the demo.
- [docs/15_ollama_backend_seam.md](/Users/riyer/code/kidschef/docs/15_ollama_backend_seam.md)
  Backend-only Ollama contract and environment configuration.
- [docs/17_local_testing_guide.md](/Users/riyer/code/kidschef/docs/17_local_testing_guide.md)
  Clear local startup, restart, verification, and demo-test instructions.

## Running Locally

Start the local server from the repo root:

```bash
./scripts/start_server.sh
```

Copy `.env.example` to `.env` and set the local Ollama model you want before starting the server.

To restart and keep logs in a file:

```bash
./scripts/restart_server.sh
```

To tail the log:

```bash
./scripts/tail_server_log.sh
```

Then open:

```text
http://127.0.0.1:8000
```

Optional:

```bash
python3 server.py --host 0.0.0.0 --port 8000
```

That exposes the app on the local network for iPhone Safari testing.

## Verification

Current lightweight verification targets are:

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `python3 -m compileall -q kidschef kidschef_backend tests server.py`
- `node --check web/app.js`

## Current Limits

This is still an MVP skeleton, not the full product contract.

Not implemented yet:

- local AI integration behind the documented AI boundary
- parent dashboard UI and analytics views
- pedagogy-derived step transformation separate from canonical recipe steps
- deeper QA automation across device and degraded-mode paths
- installable PWA behavior and offline cache policy

The current shape is intentionally conservative: deterministic data and safety first, then AI and richer product layers on top.
