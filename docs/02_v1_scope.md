# KidsChef V1 Scope

## Purpose

KidsChef v1 is a kid-facing, mobile-first web app for ages 10-14 that helps a child pick a meal idea, enter ingredients they already have, filter by allergies and dietary needs, and receive one safe recipe at a time with step-by-step guidance.

The app must run well on iPhone Safari from a local networked machine, use local AI where possible, and keep child safety and privacy ahead of novelty.

## In Scope

- Meal categories: breakfast, lunch, dinner, snack
- Kid-facing entry flow for ingredients on hand
- Allergy and dietary filters
- Recipe suggestions from a mix of curated content and local AI
- One-recipe-at-a-time experience
- One-step-at-a-time instructions with large controls
- Timers embedded in steps where useful
- Favorites
- Age-based safety modes
- Adult-help markers for risky steps
- Blocking unsafe recipes, including knife-heavy recipes and recipes that require stove or oven use for younger kids
- Calm, educational UI with light game-like rewards
- Local-only operation with no accounts
- Parent visibility for supervision and trust
- Analytics limited to what is needed to improve the product locally

## Safety And Privacy Rules

- Safety overrides convenience.
- Privacy overrides personalization depth.
- If a requirement is ambiguous, choose the stricter interpretation.
- If local AI can answer safely, use it.
- If remote AI is required, parent supervision is mandatory.
- Do not allow user-generated content in v1.
- Do not use paid APIs unless they are explicitly approved LLM access.

## Out Of Scope For V1

- User accounts or sign-in
- Social features
- Open-ended community uploads or sharing
- Ads or monetization flows
- Full offline support without a local host machine
- Native iPhone app
- Multi-device sync outside the local household network
- General-purpose cooking chat with no safety guardrails
- Advanced gamification that competes with recipe clarity
- Broad recipe editing or publishing tools

## Decision Rules

- Product ambiguity is resolved by Product Triage.
- Child safety and remote AI supervision are resolved by Safety and Policy.
- Recipe teaching quality is resolved by Recipe Pedagogy.
- Recipe data shape is resolved by Data and Content.
- If a feature adds complexity without improving a child’s ability to complete a safe recipe, defer it.

## Open Questions Handling

- Open questions are tracked separately in [04_open_questions.md](/Users/riyer/code/kidschef/docs/04_open_questions.md).
- This document is the committed v1 contract.
- If a requirement is not stated here and is still under debate, it is not in scope until Product Triage records a decision.

## V1 Success Criteria

- A child can choose a meal type, enter ingredients, and receive a safe recipe suggestion.
- The recipe can be followed step by step on iPhone Safari.
- Unsafe suggestions are blocked or downgraded before they reach the child.
- Favorites and basic reward feedback work without making the product noisy.
- The app functions locally without accounts and respects child privacy constraints.
