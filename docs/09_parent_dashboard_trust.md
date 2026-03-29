# KidsChef Parent Dashboard and Trust Contract

## Purpose

The parent dashboard is a local, privacy-sensitive supervision surface for KidsChef v1. Its job is to help a parent understand what the child is doing, adjust household safety settings, review limited local analytics, and supervise any remote-AI fallback.

It is not a child co-pilot, content editor, or social account area.

## Scope

### In Scope

- household safety mode visibility and update
- supervision of remote-AI sessions
- limited local analytics summaries
- recent child activity summaries
- favorites and repeated recipe usage at a household level
- privacy-visible controls for retention and local data reset

### Out Of Scope

- accounts or sign-in
- multi-household profiles
- social sharing
- unrestricted child chat transcripts
- manual recipe publishing or editing tools
- ad-tech, tracking pixels, or cloud analytics

## Supervision Boundaries

### Default Rule

Local AI is preferred. Remote AI is only allowed when `Safety and Policy` permits it and a parent is actively supervising.

### Remote-AI Handling

When a request requires remote AI:

1. The backend must mark the session as `supervised`.
2. The parent dashboard must surface the request before the child sees the result.
3. The parent must explicitly approve or continue the session.
4. The resulting output must still pass the safety policy gate.

If supervision is not available, the system must block remote AI rather than silently fall back to an unsupervised path.

### Safety-Sensitive Surfaces

The dashboard may show and control:

- the selected household safety mode
- whether remote AI is permitted
- whether a supervised session is active
- whether a recipe or AI response was blocked for safety
- whether adult help was required for a step

The dashboard must not weaken the child safety rules defined in the safety policy.

## Parent-Visible Controls

The dashboard may expose these privacy-visible controls:

- set or review household safety mode
- enable or disable remote-AI fallback for the household
- clear local analytics history
- clear cached local recipe/session data
- review what categories of data are retained locally
- review whether favorites are stored household-shared or device-scoped once that product decision is finalized

Controls that materially affect child-visible safety behavior must go through the same validation path as child-flow policy changes.

## Allowed Visibility Into Child Activity

The parent may see only the minimum information needed for trust and supervision:

- meal category chosen
- recipe title or recipe category shown
- whether a recipe was started, completed, favorited, or abandoned
- whether a safety block occurred
- whether adult help was requested or required
- whether a timer was used
- whether a supervised remote-AI request occurred
- household-level trends such as common meal types or repeated favorites

The parent should not receive raw child input by default unless the specific feature requires it for supervision and it is still privacy-minimal.

## Local Analytics Limits

Analytics for the dashboard must be local-first and minimal:

- store data on the household host only
- do not send child telemetry to third parties
- retain only what is needed for recent activity, household summaries, and debugging
- prefer aggregated counts over event-by-event histories when possible
- avoid free-form child chat retention
- avoid behavioral profiling beyond what is needed for trust and product feedback

If analytics are ambiguous, choose the smallest useful dataset.

## Privacy-Visible Data Controls

The dashboard must make data handling understandable to a parent:

- show what is retained locally
- show what can be cleared
- show whether a feature depends on local storage or live backend data
- show whether remote AI is available only under supervision
- show whether the household host is the only persistence location

The UI should explain these controls in plain language, not policy jargon.

## Dashboard UX Rules

- The dashboard should be available from the same local web app, but visually separated from the child flow.
- The parent surface should be read-heavy and low-friction.
- Parent actions that affect safety should be explicit and confirmable.
- Parent views should not interrupt an active child session unless supervision is required.
- The dashboard should prioritize clarity over detail density.

## Non-Goals For V1

- full account management
- remote cloud sync
- detailed child analytics timelines
- parental messaging or notes
- shared family social features
- recipe authoring tools
- unrestricted transcript review
- any analytics export outside the household host

## Contract For Other Teams

- `Safety and Policy` defines the supervision gate and veto rules.
- `Backend and Local Runtime` owns local analytics storage, summaries, and parent API shape.
- `Web Platform` owns the dashboard shell and route structure.
- `Product Triage` resolves any ambiguity about how much visibility is justified.

If the dashboard needs more visibility than this contract allows, it is a new product decision, not a UI tweak.

