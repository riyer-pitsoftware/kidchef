# KidsChef Safety Policy

## Purpose

This policy defines the safety and privacy rules for KidsChef v1. It overrides product preference, UX convenience, and AI creativity when those conflict with child safety or privacy.

## Safety Modes

KidsChef uses age-based safety modes. Modes are set by age profile and can only be changed by a parent or Product Triage decision.

- `strict`: default for ages 10-11
- `standard`: default for ages 12-14
- `supervised`: remote AI mode that is only allowed when a parent is actively supervising

If age is unknown, default to `strict`.

## Hard Restrictions

The system must block any recipe or step that violates these rules:

- No knife-heavy recipes for `strict` mode.
- No stove or oven steps for `strict` mode.
- Any knife, stove, or oven step in `standard` mode must be explicitly marked as adult help and must not be presented as child-only work.
- If the app cannot confidently determine that a step is safe for the selected mode, it must treat the step as unsafe.
- If a recipe depends on unavailable appliances or unsafe substitutions, it must be blocked or downgraded.

## Allergy And Dietary Enforcement

- Allergy and dietary filters are mandatory safety gates, not preferences.
- A recipe that includes a blocked allergen, dietary conflict, or ambiguous ingredient match must not be shown as a primary recommendation.
- If a safer variant exists, downgrade to that variant.
- If no safe variant exists, block the recipe and suggest alternatives that satisfy the same meal type.

## Adult-Help Markers

- Any step involving heat, sharp tools, heavy lifting, or other age-sensitive action must be marked with an adult-help indicator when allowed at all.
- Adult-help markers must be visible before the child starts the step.
- Adult-help steps cannot be hidden inside vague language or buried in a paragraph.

## Local Vs Remote AI

- Local AI is the default and preferred path.
- Remote AI may only be used when local AI is unavailable or a feature explicitly requires it.
- Remote AI cannot interact with a child unsupervised.
- If remote AI is used, the session must run in `supervised` mode and a parent must be present or explicitly engaged.
- Any remote AI output must still pass through the safety policy gate before it is shown.

## Privacy Guardrails

- No accounts in v1.
- No ads.
- No user-generated content.
- Collect the minimum data needed for recipes, safety, and local household operation.
- Prefer local storage and local processing over network transmission.
- Do not retain free-form child chat content longer than needed to complete the request.
- Analytics, if enabled, must be privacy-minimal and local-first.

## Blocking And Downgrading Rules

When evaluating a recipe or AI response:

1. Block immediately if it violates a hard restriction, a blocked allergen, or remote-AI supervision rules.
2. Downgrade if the recipe can be made safe by swapping appliances, splitting steps, adding adult-help markers, or simplifying instructions.
3. If the safe downgrade still leaves ambiguity, block it.
4. If local AI produces an unsafe or unstructured answer, discard it and regenerate from the constrained recipe schema.
5. If a recipe cannot be made safe for the selected mode, do not show it to the child.

## Operational Decision Rules

- Safety always wins over delight, novelty, or recommendation quality.
- Choose the stricter interpretation when a rule is unclear.
- Prefer blocking over guessing when the model or metadata is incomplete.
- Prefer curated, deterministic output over open-ended generation when safety is at stake.
- Escalate unresolved safety ambiguity to Safety and Policy before implementation or release.

## Ownership

Safety and Policy owns this policy and has veto power over any behavior that weakens child safety, supervision, or privacy.
