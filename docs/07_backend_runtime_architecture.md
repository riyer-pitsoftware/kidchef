# KidsChef Backend and Household Runtime Architecture

## Purpose

This document defines the v1 backend and runtime shape for a single-household KidsChef deployment. It fixes service boundaries for local network use, clarifies persistence ownership, and defines how the system behaves when network, AI, or storage dependencies are degraded.

This document follows the constraints in [00_init_survey.md](/Users/riyer/code/kidschef/docs/00_init_survey.md), [02_v1_scope.md](/Users/riyer/code/kidschef/docs/02_v1_scope.md), [03_ambiguity_workflow.md](/Users/riyer/code/kidschef/docs/03_ambiguity_workflow.md), and the open questions in [04_open_questions.md](/Users/riyer/code/kidschef/docs/04_open_questions.md).

## Deployment Shape

KidsChef v1 runs as a single local household host on the home network.

- One household machine hosts the web app, local backend APIs, local persistence, and local AI integration.
- iPhones and other household devices connect to that machine over the local network through Safari.
- No cloud account, public internet dependency, or external identity service is required for the core child flow.
- Remote AI, if allowed at all, is a supervised fallback path and is outside the default runtime contract.

The default topology is:

1. `kidschef-web`: serves the child UI and parent dashboard UI.
2. `kidschef-api`: serves application APIs for recipes, favorites, household preferences, analytics intake, and parent dashboard reads.
3. `kidschef-store`: local persistence for curated recipes, derived recipe records, favorites, household settings, and analytics events.
4. `kidschef-ai-bridge`: local-only integration boundary for structured recipe recommendation and recipe generation.

These components may run in one process for v1, but the service boundaries must remain explicit in code and API design so other teams can plan against stable contracts.

## Service Boundaries

### 1. Web App Boundary

The web layer owns:

- kid-facing meal selection, ingredient entry, filters, guided recipe flow, and favorites interactions
- parent dashboard views
- local caching needed for responsiveness and partial offline behavior

The web layer does not own:

- recipe safety decisions
- canonical favorites persistence
- analytics storage
- direct model orchestration

### 2. Application API Boundary

The backend API is the canonical household application layer. It owns:

- recipe query and retrieval APIs
- favorites write and read APIs
- household preference APIs for allergies, dislikes, skill level, and appliance availability
- analytics intake APIs
- parent dashboard read APIs
- orchestration across curated content, persistence, and local AI

The backend API must expose deterministic contracts even when AI-backed recommendation quality varies.

### 3. Persistence Boundary

The local store is the canonical source for household data. It owns:

- curated recipe records and metadata needed for safe filtering
- AI-derived recipe records once accepted into the app response flow
- favorites
- household safety mode and preference state
- analytics events and derived summary tables used by the parent dashboard

The local store does not own transient UI state such as current step position during an active session unless the product later decides that recovery across reloads is required.

### 4. Local AI Boundary

The AI bridge is a bounded internal service. It owns:

- calling the local model runtime
- applying structured prompts and output schemas
- returning recommendation candidates or recipe drafts in a machine-validated shape
- surfacing AI availability and confidence state to the backend

The AI bridge does not own:

- final safety approval
- final ranking shown to the child
- persistence decisions
- parent supervision policy

All AI outputs must flow back through backend policy checks before reaching the child UI.

## Persistence Responsibilities

### Recipe Storage

Recipe persistence is split into two responsibilities:

- Curated recipe library: canonical local dataset with safety metadata, allergy tags, appliance tags, skill tags, and meal-type classification.
- Derived recipe cache: AI-suggested or AI-transformed recipe records that pass validation and are stored locally so they can be reused, inspected, and explained.

Recipe storage must preserve enough metadata for:

- safety filtering before display
- appliance and skill-based personalization
- parent-visible explanation of why a recipe was shown or blocked
- degraded-mode fallback to curated content when AI is unavailable

### Favorites and Household Preferences

Favorites and household preferences are backend-owned household state, not client-owned state.

- Favorites are stored in the local backend store as household-local records.
- Allergy, diet, disliked ingredient, skill level, appliance availability, and safety mode preferences are stored in the same local backend store.
- The web app may cache recent favorites and preferences for responsiveness, but the cache is not authoritative.

The open question of whether favorites are per-device or shared across devices is unresolved. Until Product Triage decides otherwise, the backend contract should support household-shared favorites while allowing the UI to present them simply.

### Analytics

Analytics are local and minimal. The backend owns analytics intake, storage, retention policy, and aggregation.

Allowed analytics responsibilities:

- log recipe impressions, recipe starts, recipe completions, favorites actions, timer usage, and safety-block events
- produce parent dashboard summaries from local-only data
- support product-quality debugging within the household host

Disallowed analytics responsibilities:

- third-party telemetry
- ad-tech identifiers
- cross-household comparison
- detailed behavioral profiling beyond what is needed for local product feedback and parent visibility

## Parent Dashboard API Responsibilities

The parent dashboard is a read-heavy trust surface with limited settings writes. The backend APIs for it own:

- household safety mode read and update
- visibility into recent recipe activity and completion counts
- visibility into favorites and repeated recipe usage
- visibility into safety blocks, adult-help markers encountered, and supervised-AI prompts
- local analytics summaries that explain recommendation and safety behavior at a household level
- privacy-visible configuration for what data is retained locally

The parent dashboard API does not own:

- direct child-flow orchestration
- free-form content editing
- remote account management

If a future parent action can materially change child-visible safety behavior, that action must pass through the same policy validation used by the child flow.

## Request Flow

The standard v1 recipe recommendation path is:

1. Child UI sends meal type, ingredients on hand, and active household filters to `kidschef-api`.
2. The API loads household preferences and safety mode from the local store.
3. The API filters curated recipes first using deterministic safety and diet rules.
4. The API optionally requests recommendation candidates from `kidschef-ai-bridge`.
5. The API validates AI results against recipe schema and safety policy.
6. The API ranks the final safe set and returns one recipe-at-a-time data to the child UI.
7. The API records minimal local analytics for the request and resulting outcome.

This ordering is intentional: safety and deterministic filtering happen before or around AI enrichment, not after the UI has already received content.

## Local Household Runtime Assumptions

- The host machine is trusted household infrastructure but should still minimize exposed ports and services.
- Household devices are semi-trusted clients; they should not be treated as authoritative sources for safety state or analytics state.
- The local network may be intermittent; the app should assume reconnects happen.
- The local AI runtime may be slow, unavailable, or resource-constrained.
- The backend must start and serve curated recipe flows even if AI is unavailable.

## Degraded-Mode Assumptions

### If Local AI Is Unavailable

- The app continues serving curated recipes and previously accepted derived recipes from local storage.
- Ingredient-based recommendations may become less personalized or narrower.
- Open-ended AI chat is disabled rather than replaced with unsafe fallback behavior.
- The UI should present a simple fallback explanation, not an error-heavy experience.

### If The Household Host Loses Internet

- Core local flows continue if the household host, local backend, and local AI runtime are still available.
- Any remote AI fallback path is unavailable.
- Parent dashboard access on the local network still works against local data.

### If A Client Device Temporarily Disconnects From The Household Host

- The web app may continue showing already loaded recipe content and cached UI shell assets.
- New recommendations, favorites writes, analytics submission, and parent dashboard refreshes are unavailable until reconnect.
- The client must treat backend writes as failed until acknowledged by the local API.

### If Persistence Is Temporarily Unavailable Or Corrupt

- The app should fail closed on writes that affect safety-relevant preferences.
- The app should not invent defaults that weaken allergies, diet filters, or safety mode.
- If recipe storage cannot be trusted, recommendation responses should degrade to a clear unavailable state rather than serve unverified content.

## Non-Goals For This Architecture

- public-cloud multi-tenant backend design
- cross-household sync
- account-based identity
- unrestricted remote AI orchestration
- user-generated recipe publishing

## Stable Contracts For Adjacent Teams

- `Data and Content` can assume the backend is the canonical owner of recipe records and metadata persistence.
- `Web Platform` can assume a local-network HTTP API with offline-tolerant read behavior but backend-authoritative writes.
- `Local AI` can assume a structured internal contract that returns candidate recipes or recommendation features, not final child-visible decisions.
- `Parent Dashboard and Trust` can assume local summary APIs over household activity, safety events, and retention-visible settings.
- `QA and Device Reliability` can assume explicit degraded-mode behavior for AI loss, host offline, client disconnect, and persistence failure.

## Open Questions Kept Explicit

This architecture intentionally does not resolve these product questions:

- the exact younger-age threshold within the 10-14 range
- whether remote AI is present in v1 or only documented as a supervised fallback
- the exact minimum analytics retention needed for the parent dashboard
- whether favorites are presented as device-local or household-shared in the UI
- how far partial offline recommendation flows go beyond previously loaded and curated content

Until those are decided, backend contracts should stay conservative, local-first, and safety-first.
