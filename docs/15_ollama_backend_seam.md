# KidsChef Ollama Backend Seam

## Purpose

This note defines the first optional Ollama-backed backend seam for KidsChef v1.

The browser never talks to Ollama directly. Ollama is only reachable from the backend, and only when explicitly enabled by environment configuration.

## Environment Variables

- `KIDS_CHEF_OLLAMA_ENABLED`
  - `true` or `false`
  - defaults to `false`
- `KIDS_CHEF_OLLAMA_HOST`
  - defaults to `http://127.0.0.1:11434`
- `KIDS_CHEF_OLLAMA_MODEL`
  - defaults to `llama3.2`
- `KIDS_CHEF_OLLAMA_TIMEOUT_SECONDS`
  - defaults to `5`
- `KIDS_CHEF_OLLAMA_MAX_CANDIDATES`
  - caps the number of recipes sent to Ollama for ranking

## Contract

- Ollama is optional.
- The backend must keep returning deterministic curated results when Ollama is disabled or unavailable.
- The Ollama seam may only rank already-safe candidate recipes.
- Ollama output must not bypass safety filtering or schema validation.
- If Ollama returns an invalid response, the backend must fall back to the deterministic ranking path.

## Response Shape

The backend recommendation response may include an `ai_assistance` object with:

- `status`
- `provider`
- `model`
- `host`
- `used`
- `ranked_recipe_ids`
- `reasons_by_recipe_id`
- `note`

These fields are additive and optional for clients.
