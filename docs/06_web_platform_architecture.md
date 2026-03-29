# KidsChef Web Platform Architecture

## Purpose

This document defines the web platform contract for KidsChef v1. It covers the mobile-first shell, frontend structure, state and storage assumptions, local-network connectivity, degraded mode boundaries, and the runtime events other teams can target.

The target is a kid-facing web app that runs well on iPhone Safari from a local household machine.

## Platform Scope

### Supported

- iPhone Safari as the primary mobile browser
- A local-network web app served from a household machine
- Tablet and desktop browsers as secondary surfaces for the same web app
- One-step recipe flows, timers, and large touch targets
- Local storage for lightweight client state

### Not Supported In The Web Shell

- Native iPhone app behavior
- Sign-in or account management
- Multi-household cloud sync
- Browser-only source of truth for durable recipe or preference data
- Direct browser-to-LLM calls

## Shell Architecture

The frontend should be a single web app with these layers:

1. `App Shell`
2. `Route-Level Screens`
3. `Shared UI Primitives`
4. `State and Data Access`
5. `Device and Network Adaptation`

### App Shell

The shell owns:

- global navigation
- responsive layout
- safe area handling
- loading and error states
- persistent player controls such as back, timer, and home

The shell must stay simple and predictable on a phone-sized viewport. Primary navigation should never require hovering or multi-step menus.

### Route-Level Screens

The initial screen set should map to the v1 flow:

- meal picker
- ingredient entry
- filter selection
- recipe suggestion results
- recipe detail and stepper
- favorites
- parent visibility screens surfaced through the same web app shell

### Shared UI Primitives

Build once, reuse everywhere:

- large button
- step card
- timer chip
- safety badge
- ingredient token
- filter pill
- empty state
- error state

These primitives must be designed for one-handed phone use first.

## Interaction Model

### Core Navigation Rules

- One primary action per screen.
- Step flow is linear by default.
- Back navigation must preserve the child’s progress.
- Timers must remain visible while a step is active.
- Safety warnings must interrupt the flow clearly and must not be hidden inside secondary panels.

### Responsive Rules

- Mobile layout is the default.
- Desktop layout may expand spacing, but it should not introduce extra interaction depth.
- Touch targets must be large enough for child use.
- Do not depend on hover, fine pointer precision, or keyboard-only workflows.

## State Model

### Client State

Client state should be split into three tiers:

- `Ephemeral UI state`: current route, open modals, active timer, scroll position
- `Session state`: current meal search, ingredient draft, selected filters, current recipe step
- `Durable local cache`: last viewed recipes, last loaded catalog snapshot, cached assets, last successful sync metadata

### Server State

The household machine is the source of truth for durable product data:

- recipe catalog
- local kid preferences
- favorites
- parent-visible analytics
- safety decisions
- AI-generated suggestions that have passed policy checks

The browser may mirror some of this data for speed, but it must not be the authoritative store.

### Storage Assumptions

- Use browser storage only for low-risk, recoverable data.
- Use IndexedDB for structured cache when durable client caching is needed.
- Use `localStorage` only for tiny preferences or boot-time flags.
- Do not store sensitive child data in uncontrolled browser caches.
- Treat the server as canonical for anything that should survive browser refreshes or device changes on the local network.

## Connectivity Assumptions

### Local Network

- The app is served by a household machine on the local network.
- iPhone Safari reaches the app over LAN without requiring public cloud access.
- The UI must tolerate temporary latency and reconnection.
- Connectivity to the local host is expected for the main v1 experience.

### Backend Boundaries

- The browser talks to the local backend over same-origin or a clearly defined local API base URL.
- The browser does not call model providers directly.
- All AI requests, content lookups, and safety checks flow through backend services.
- If remote AI is ever enabled, the backend must enforce the parent supervision requirement before the browser sees the result.

## Safari Constraints

The primary browser target is current iPhone Safari. The frontend must assume:

- no hover-dependent controls
- no requirement for persistent background execution
- timer UX may be interrupted when Safari backgrounds the page or the device locks
- storage is useful for caching, but the browser is not the durable source of truth
- installability and offline behavior are progressive enhancements, not product guarantees

The product must still behave clearly when Safari suspends background work, clears recoverable cache, or reconnects after the device returns to the foreground.

## Offline And Degraded Mode

### Allowed Offline Behavior

The web app should continue to function in a limited way if the local host becomes temporarily unavailable after initial use:

- show cached shell assets
- show last visited recipes that were cached locally
- preserve in-progress UI drafts if the browser can do so safely
- explain that live suggestions are unavailable

### Not Allowed Offline Behavior

- generating new recipe recommendations from scratch
- changing durable household data
- making safety decisions without the backend policy layer
- pretending stale data is current

### Degraded Mode UX

When the backend is unavailable, the UI should switch to a clear degraded state:

- explain what still works
- hide actions that cannot complete safely
- retain the child’s place in the flow when possible
- provide a simple reconnect action

## UI Runtime Contracts

Other teams can build against these runtime contracts.

### Screen Contracts

- Each screen declares a single primary action.
- Each recipe step screen exposes `next`, `back`, `repeat step`, and `timer` behaviors.
- Each filter screen returns a structured filter selection object.
- Each suggestion screen can render both AI-generated and curated results through the same card interface.

### Event Contracts

The frontend should emit stable events with typed payloads:

- `meal_type_selected`
- `ingredients_updated`
- `filters_updated`
- `recipe_suggested`
- `recipe_selected`
- `step_started`
- `step_completed`
- `timer_started`
- `timer_finished`
- `favorite_toggled`
- `safety_warning_shown`
- `ai_request_started`
- `ai_request_blocked`
- `backend_unavailable`

### Data Contracts

The UI expects recipe data to include:

- title
- meal type
- ingredient list
- step list
- timer metadata
- adult-help markers
- safety level
- appliance tags
- allergy tags
- provenance such as `curated` or `ai-assisted`

The UI should not infer safety metadata from free text alone.

### Error Contracts

Every feature screen must support:

- empty state
- loading state
- retry state
- blocked-by-safety state
- backend-unavailable state

## Implementation Guidance

- Keep frontend data-fetching thin and centralized.
- Keep route transitions deterministic.
- Prefer simple component composition over deeply nested conditional rendering.
- Make safety and connectivity failures obvious, not subtle.
- Design the shell so UX, AI, and backend teams can change their own contracts without rewriting the app navigation.
