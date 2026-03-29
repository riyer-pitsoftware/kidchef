# KidsChef Agentic Team Plan

## Goal

Set up an agentic team to build a mobile-first KidsChef app for ages 10-14 that works well on iPhone Safari from a local networked machine, teaches recipes step by step, uses local AI where possible, and treats child safety and privacy as hard constraints.

This plan is based on [00_init_survey.md](/Users/riyer/code/kidschef/docs/00_init_survey.md).

## Product Constraints Driving Team Design

- Primary user is the kid, not the parent.
- Target age is 10-14.
- Core v1 flow is breakfast/lunch/dinner/snack selection, ingredient entry, allergy and diet filtering, guided cooking, and favorites.
- Recipe guidance must be one step at a time with large controls and timers.
- Safety rules are central to the product: age-based safety modes, adult-help markers, and exclusion of unsafe recipes.
- Recipe intelligence is a mix of curated content plus local AI suggestions.
- No accounts in v1. The product is local-use and privacy-sensitive.
- The first delivery target is a web app that runs on a local machine and is usable on iPhone Safari over the local network.
- The app must tolerate vague and conflicting requirements without agents drifting into unsafe or over-scoped decisions.

## Recommended Team

This is the smallest team that still preserves safety, clarity, and parallel execution. Some people can hold multiple roles later, but the roles should remain explicit.

### 1. Product Triage Agent

Owns vague or conflicting requirements, writes decision records, defines acceptance criteria, and decides what is in or out of v1.

Why this role exists:
- This product already has tension between calm UX and gamification, local-only constraints and AI richness, and safety versus autonomy.
- Without explicit ownership, implementation agents will silently make product decisions.

### 2. Kid UX Agent

Owns the kid-facing experience:
- mobile-first UI
- iPhone Safari ergonomics
- large tap targets
- one-step recipe flow
- timer interactions
- readable language for ages 10-14
- calm educational visual direction

### 3. Recipe Pedagogy Agent

Owns how recipes are taught:
- skill-level mapping
- step simplification
- teachable sequencing
- appliance adaptations
- adult-help markers within instructions
- confidence-building progression

### 4. Safety and Policy Agent

Owns all hard constraints:
- age-based safety modes
- knife, stove, and oven restrictions
- allergy and diet enforcement
- local versus remote AI supervision rules
- privacy boundaries

This role has veto power over launches and feature behavior that violate safety or privacy policy.

### 5. Data and Content Agent

Owns the structured recipe/content model:
- curated recipe ingestion
- recipe schema
- safety metadata
- allergy tags
- appliance metadata
- skill tags
- content normalization for both UI and AI use

### 6. Web Platform Agent

Owns the app shell and client runtime:
- web-first mobile architecture
- iPhone Safari support
- navigation shell
- local storage primitives
- PWA/service worker boundaries
- core frontend foundations

### 7. Backend and Local Runtime Agent

Owns the local networked backend:
- recipe storage
- favorites and local profile persistence
- analytics ingestion
- parent dashboard APIs
- local AI service boundaries
- deployment topology for a single local household machine

### 8. Local AI Agent

Owns constrained AI behavior:
- local LLM orchestration
- prompt and structured output contracts
- recommendation logic
- ingredient-based suggestions
- fallback behavior when local AI is unavailable
- ensuring AI passes through the safety policy layer

This role does not own safety policy. It consumes it.

### 9. Parent Dashboard and Trust Agent

Owns parent-facing trust surfaces:
- dashboard UX
- local analytics views
- supervision prompts
- explanations for recommendation and safety decisions
- privacy-visible controls

### 10. Gamification Agent

Owns rewards and motivation:
- badges
- streaks
- levels
- stars for trying new foods

This role is intentionally separate from Kid UX so the product stays calm and educational rather than over-stimulating.

### 11. QA and Device Reliability Agent

Owns validation:
- iPhone Safari behavior
- local-network conditions
- offline and degraded mode behavior
- timer/background behavior
- regression testing for safety rules
- release checks against acceptance criteria

## Team Structure

Use the team in three layers.

### Coordination Layer

- Product Triage Agent
- Safety and Policy Agent
- QA and Device Reliability Agent

Purpose:
- define what is being built
- define what is allowed
- verify that the result is actually safe and correct

### Product Layer

- Kid UX Agent
- Recipe Pedagogy Agent
- Data and Content Agent
- Gamification Agent
- Parent Dashboard and Trust Agent

Purpose:
- define the experience, content model, motivation loops, and household trust surfaces

### Platform Layer

- Web Platform Agent
- Backend and Local Runtime Agent
- Local AI Agent

Purpose:
- make the product operational on a local machine and usable from iPhone Safari

## Decision Rights

Each task must have one explicit decision owner.

- Product scope conflicts: Product Triage Agent
- Child safety and remote AI supervision: Safety and Policy Agent
- Child-facing UI behavior: Kid UX Agent
- Recipe teaching quality: Recipe Pedagogy Agent
- Recipe schema and metadata: Data and Content Agent
- Web runtime and mobile architecture: Web Platform Agent
- Local deployment and backend services: Backend and Local Runtime Agent
- AI recommendation and generation behavior: Local AI Agent
- Parent-facing visibility and controls: Parent Dashboard and Trust Agent
- Rewards and progression: Gamification Agent
- Release readiness: QA and Device Reliability Agent

## Rules for Working Under Vague or Conflicting Requirements

All agents must follow these rules.

### Non-negotiable precedence

1. Safety
2. Privacy
3. Core task completion
4. Simplicity for ages 10-14
5. Technical feasibility under local-only constraints
6. Delight and gamification

### Required behavior

- If a requirement is vague, rewrite it into a testable statement before implementation.
- If two requirements conflict, surface the conflict explicitly and propose two options with tradeoffs.
- If AI behavior is unclear, prefer curated or deterministic behavior over open-ended generation.
- If safety behavior is unclear, choose the stricter rule.
- If scope is unclear, defer it out of v1.
- If a feature needs data that weakens privacy, store less.

### Standard decision record format

Every material ambiguity should be resolved with:

- Decision to make
- Options considered
- Recommended option
- Safety impact
- Product impact
- Deferred follow-up

## Parallel Work Plan

The team can work in parallel, but not from day one on every slice. These are the dependency boundaries.

### Phase 1: Foundations

These must start first.

- Product Triage Agent defines v1 scope, exclusions, and decision log format.
- Safety and Policy Agent defines safety rules, age modes, and remote AI supervision policy.
- Data and Content Agent defines recipe schema and metadata contracts.
- Web Platform Agent defines frontend shell, Safari constraints, and storage/API assumptions.
- Backend and Local Runtime Agent defines local deployment shape and service boundaries.

Deliverables:
- v1 scope doc
- safety policy doc
- recipe schema
- local architecture outline
- frontend contract assumptions

### Phase 2: Parallel Feature Build

Once Phase 1 contracts exist, these tracks can run concurrently.

- Kid UX Agent builds meal chooser, ingredient entry, filters, guided step flow, and favorites UI against mocked or early APIs.
- Recipe Pedagogy Agent authors step-by-step teaching rules and content transformation patterns.
- Local AI Agent builds constrained recommendation flows using the agreed schema and safety policy.
- Parent Dashboard and Trust Agent builds parent visibility and supervision flows after analytics and safety events are defined.
- Gamification Agent defines rewards that reinforce learning without interrupting cooking.
- QA and Device Reliability Agent starts device and degraded-mode test coverage early.

### Phase 3: Integration and Hardening

These tracks converge here.

- Integrate AI output through the safety policy layer.
- Verify offline and degraded mode behavior.
- Validate iPhone Safari and local-network performance.
- Reconcile calm UX with rewards.
- Verify parent dashboard visibility for safety-sensitive flows.

## Recommended Initial Task Board

Start the team with these top-level tracks:

1. Define v1 product scope and explicit non-goals.
2. Define child safety policy and AI supervision rules.
3. Define recipe/content schema and safety metadata.
4. Define local-first architecture for web, backend, and AI.
5. Define kid-facing UI flow and teaching model.
6. Define parent dashboard purpose and privacy limits.
7. Define rewards model that does not compromise cooking clarity.
8. Define QA matrix for iPhone Safari, local network, and degraded mode.

## Agent Handoff Contracts

Use these handoffs so agents do not drift.

- Product Triage -> all agents:
  accepted requirement, exclusions, acceptance criteria, open questions
- Safety and Policy -> Data, UX, AI, QA:
  policy rules, blocked content, required markers, escalation cases
- Data and Content -> UX, AI, Backend:
  recipe schema, tag definitions, canonical sample content
- Web Platform -> UX, Parent Dashboard, QA:
  app shell constraints, navigation model, state boundaries
- Backend and Local Runtime -> UX, AI, Parent Dashboard, QA:
  API contracts, persistence model, degraded-mode behavior
- Local AI -> UX, QA, Safety:
  prompt/output contracts, fallback behavior, confidence limits
- QA -> all agents:
  failing scenarios, device findings, release gate status

## Roles That Must Not Be Combined Early

- Safety and Policy with Gamification
- Kid UX with Gamification
- Product Triage with execution-heavy implementation roles
- Local AI with final safety decision ownership
- Parent Dashboard and Trust with child-facing UX ownership

These combinations create predictable drift.

## Recommended Kickoff Sequence

1. Appoint one person or one lead agent as Product Triage owner.
2. Draft the first three source-of-truth docs:
   - v1 scope
   - safety policy
   - recipe schema
3. Stand up the Platform trio in parallel:
   - Web Platform
   - Backend and Local Runtime
   - Local AI
4. Start Product-layer work against those contracts:
   - Kid UX
   - Recipe Pedagogy
   - Parent Dashboard and Trust
   - Gamification
5. Keep QA active from the start, especially for iPhone Safari and offline behavior.

## Practical Recommendation

If team size is limited, start with seven active agents instead of eleven:

- Product Triage
- Safety and Policy
- Kid UX
- Data and Content
- Web Platform
- Backend and Local Runtime
- QA and Device Reliability

Then add these as the foundations stabilize:

- Local AI
- Recipe Pedagogy
- Parent Dashboard and Trust
- Gamification

This keeps early coordination tight while preserving the critical separations between product scope, safety, data, platform, and validation.
