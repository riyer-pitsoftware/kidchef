# KidsChef Local AI Architecture

## Purpose

This document defines the local AI boundary for KidsChef v1. It covers structured recommendation and generation behavior, safety enforcement points, fallback behavior, and the minimum response shapes other teams can rely on.

The local AI service is internal to the household backend. The browser never calls an LLM directly.

## AI Responsibilities

The local AI layer may:

- rank safe candidate recipes from curated content
- suggest ingredient-based recipe candidates within the active safety mode
- transform structured recipe data into simpler child-facing wording
- return structured explanations for why a recipe was suggested or blocked
- report availability, confidence, and fallback state to the backend

The local AI layer may not:

- approve safety on its own
- persist household data
- bypass allergy, appliance, or age-based restrictions
- expose free-form child chat as the product source of truth
- write directly to client state or parent dashboard state

## Architecture

The AI path has three bounded stages:

1. `Request normalization`: the backend converts the user request, household settings, and recipe candidates into a structured prompt input.
2. `Model execution`: the local model produces structured candidate output.
3. `Policy validation`: the backend validates the result against safety policy and the recipe schema before anything reaches the child UI.

This order is deliberate. Safety and schema validation happen around AI, not after the child has already seen content.

## Structured Input Contract

The backend sends the AI bridge a structured request with at least:

- `request_id`
- `meal_type`
- `ingredients`
- `filters`
- `household_safety_mode`
- `available_appliances`
- `age_mode`
- `curated_candidates`
- `allow_remote_ai`
- `supervised_session`
- `policy_version`

### Input Rules

- `ingredients` and `filters` must already be normalized by the backend.
- `curated_candidates` should be preferred whenever enough safe options already exist.
- `allow_remote_ai` must be false unless `Safety and Policy` has already permitted supervised remote use.
- If the request is missing required safety context, the AI bridge must not guess.

## Structured Output Contract

The AI bridge returns one of three response states:

- `ok`
- `blocked`
- `unavailable`

### Recommendation Response

When `status` is `ok`, the minimal recommendation response shape is:

- `status`: `ok`
- `request_id`
- `recommendations`: ordered list of recommendation items
- `fallback_used`: boolean
- `confidence`: `low`, `medium`, or `high`
- `model_source`: `local`

Each recommendation item must include:

- `recipe_id`
- `title`
- `meal_type`
- `summary`
- `source`
- `compatibility`
- `reason`

`compatibility` must be machine-readable and may include:

- `safe_for_mode`
- `requires_adult_help`
- `blocked_by_allergy`
- `blocked_by_appliance`
- `blocked_by_age_mode`

### Recipe Draft Response

If the AI is generating a new candidate recipe, it must emit a recipe object that conforms to [08_recipe_schema.md](/Users/riyer/code/kidschef/docs/08_recipe_schema.md) plus:

- `generation_notes`
- `validation_state`

The backend may ignore `generation_notes` after validation. It may not accept an AI draft that fails schema or safety checks.

### Blocked Response

When `status` is `blocked`, the minimal response shape is:

- `status`: `blocked`
- `request_id`
- `blocked_reason`
- `fallback_used`: boolean

### Unavailable Response

When `status` is `unavailable`, the minimal response shape is:

- `status`: `unavailable`
- `request_id`
- `unavailable_reason`
- `fallback_used`: false

## Curated Vs AI Boundaries

- Curated recipes are canonical household content.
- AI may rank curated recipes, simplify them, or generate new candidates, but it does not own the canonical store.
- If curated content already satisfies the request safely, the backend should prefer it over AI generation.
- If AI and curated metadata conflict, curated metadata wins.
- AI-derived recipes become durable only after backend validation succeeds.

## Safety Enforcement Points

Safety policy must be enforced at four points:

1. Before AI invocation, to ensure the request is already allowed.
2. During AI prompt construction, to carry the active mode, blocked allergens, and appliance constraints.
3. After AI output, to validate against [05_safety_policy.md](/Users/riyer/code/kidschef/docs/05_safety_policy.md) and [08_recipe_schema.md](/Users/riyer/code/kidschef/docs/08_recipe_schema.md).
4. Before UI delivery, to block or downgrade anything still ambiguous.

If any check fails, the backend must discard the AI output and use a safe fallback.

## Fallback Behavior

### If Local AI Is Unavailable

- Return `unavailable`.
- Serve curated recipes and previously validated derived recipes only.
- Do not invent an unsupervised fallback path.

### If AI Output Is Unsafe

- Return `blocked` or reject the output internally.
- Do not show partial unsafe content.
- Retry only if the backend can tighten the request without weakening safety.

### If Remote AI Is Required

- Treat the request as `supervised` only.
- Require the parent supervision gate before the child sees the result.
- If supervision is not present, block the request rather than escalating silently.

## Minimal Response Shapes Other Teams Can Rely On

### For `Backend and Local Runtime`

The backend can rely on:

- `status`
- `request_id`
- `recommendations` when `status` is `ok`
- `blocked_reason` when `status` is `blocked`
- `unavailable_reason` when `status` is `unavailable`
- `fallback_used`

### For `Kid UX`

The UI can rely on:

- `recipe_id`
- `title`
- `meal_type`
- `summary`
- `source`
- `compatibility`
- `reason`

The UI must not depend on raw model text or hidden reasoning.

### For `Safety and Policy`

Safety review can rely on:

- the structured request inputs
- the compatibility flags
- the final recipe schema output
- explicit blocked or unavailable states

### For `QA and Device Reliability`

QA can exercise these stable outcomes:

- safe recommendation returned
- safe recommendation blocked
- AI unavailable with curated fallback
- supervised remote-AI blocked when supervision is missing

## Non-Goals

- direct browser-to-LLM calls
- open-ended child chat as a product surface
- free-form model reasoning exposure
- cross-household model memory
- model training or fine-tuning in v1

## Ownership

Local AI owns orchestration and structured output behavior within the safety policy. It does not own final safety approval or persistence decisions.
