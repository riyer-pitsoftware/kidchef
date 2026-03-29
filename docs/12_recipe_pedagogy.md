# KidsChef Recipe Pedagogy Guide

## Purpose

This guide defines how KidsChef teaches recipes to ages 10-14 in v1. It covers step writing, language simplification, confidence-building progression, adult-help signaling, appliance adaptations, and the transformation from canonical recipe records into kid-friendly guided flows.

This guide consumes the contracts in [02_v1_scope.md](/Users/riyer/code/kidschef/docs/02_v1_scope.md), [05_safety_policy.md](/Users/riyer/code/kidschef/docs/05_safety_policy.md), [08_recipe_schema.md](/Users/riyer/code/kidschef/docs/08_recipe_schema.md), and [09_parent_dashboard_trust.md](/Users/riyer/code/kidschef/docs/09_parent_dashboard_trust.md).

## Teaching Priorities

When teaching rules compete, choose in this order:

1. safety clarity
2. task completion
3. simplicity for ages 10-14
4. confidence building
5. speed and compactness

If a recipe cannot be taught clearly under these priorities, it should be split, downgraded, adapted, or blocked rather than shown in a confusing form.

## One-Step-At-A-Time Rules

Every child-facing guided flow must present exactly one action step at a time.

- Each screen should ask the child to do one main thing, not interpret a paragraph.
- A step may include a short supporting note, but not a second hidden action.
- If a canonical step contains `and`, `then`, `while`, or multiple tool changes, split it into multiple guided steps.
- Ingredient gathering, measuring, mixing, appliance use, waiting, checking, and serving should be separated when that makes the flow easier to follow.
- Timer steps should be independent steps or clearly attached to one active action, never buried inside a long instruction.
- A child should be able to read the step once and know what to do next without scanning the ingredient list again.

Good:

- "Put the yogurt in the bowl."
- "Sprinkle the cinnamon on top."
- "Start the 60-second timer."

Bad:

- "Put the yogurt in a bowl, add cinnamon, stir well, and wait one minute before serving."

## Language Simplification Rules For Ages 10-14

Child-facing instructions must use plain, concrete language.

- Prefer common kitchen words over culinary jargon.
- Use short sentences.
- Start with a verb.
- Name the tool or ingredient the child should touch next.
- Use exact quantities only when they help the child act safely or correctly.
- Replace vague phrases like "prepare," "process," or "finish as needed" with visible actions.
- Avoid idioms, sarcasm, and abstract encouragement that obscures the task.
- Avoid dense safety text inside the main instruction. Put the warning in the adult-help or warning field.

Preferred wording patterns:

- "Put"
- "Mix"
- "Open"
- "Press"
- "Wait"
- "Ask an adult to help"
- "Check if it looks warm and melted"

Avoid wording patterns:

- "Incorporate"
- "Agitate until combined"
- "Proceed cautiously"
- "Cook appropriately"

## Confidence-Building Progression

KidsChef should teach toward independence, not just completion.

- Early steps in a recipe should favor easy wins such as gathering, pouring, stirring, or choosing.
- More delicate or safety-sensitive actions should happen later and only when clearly prepared for.
- Recipes for lower skill levels should use more confirmation steps, such as "Now check that the bread is in the toaster."
- Step text should emphasize what success looks like in observable terms.
- Praise, if present, should be brief and calm. It should not interrupt the cooking flow.
- The guided flow should reduce hidden decisions. Do not ask a child to improvise unless the recipe explicitly allows a simple choice.

The teaching model should map broadly to these progression levels:

- `independent_beginner`: safe, concrete actions with minimal judgment required
- `guided_beginner`: simple actions plus a few checks, timers, or adult-help moments
- `developing`: more sequencing, optional variations, and appliance awareness, still under explicit guidance

If a recipe would require too much judgment for its labeled skill level, raise the skill level, add more guided steps, or block it.

## Adult-Help Signaling Rules

Adult-help signaling must be explicit before the child reaches the risky action.

- Any step with heat, sharp tools, heavy lifting, or uncertain safety must be marked before the action is shown.
- Do not hide adult-help inside the middle or end of a sentence.
- The child-facing instruction should say the action and the need for help plainly.
- The UI should surface adult-help visually and textually using the structured safety fields from the recipe schema.
- If a canonical step is `adult_help`, the pedagogy layer may split it into prep and help-required substeps, but it may not downgrade the risk.

Preferred patterns:

- "Ask an adult to help with the microwave."
- "Wait for an adult before this step."
- "An adult should do the knife part."

Disallowed patterns:

- "Carefully handle the knife."
- "Use caution around the hot dish."

Those phrases shift judgment onto the child instead of making the supervision requirement explicit.

## Appliance Adaptation Rules

Appliance adaptations should preserve the meal outcome while reducing risk and cognitive load.

- Prefer the safest allowed appliance path for the active safety mode.
- If multiple appliance variants exist, choose the one with the fewest risky transitions.
- Appliance-specific wording must name the appliance and what the child should expect.
- If an appliance requires adult help in the active mode, signal that before the step.
- If a recipe can be adapted from stove or oven to microwave, toaster, or air fryer without weakening safety or clarity, prefer the safer variant.
- If the adaptation changes timing or texture expectations, add a check step so the child knows what success looks like.

Examples:

- Replace "Saute on the stove for 5 minutes" with a microwave or no-cook alternative when the recipe model allows it.
- Replace "Bake until done" with "Cook in the air fryer for 6 minutes, then check if the cheese is melted."

If a safe appliance adaptation cannot be expressed clearly, block or downgrade the recipe rather than forcing an unsafe translation.

## Canonical Recipe To Guided Flow Transformation

The pedagogy layer transforms a validated canonical recipe into a guided child flow. It does not create new unsafe capabilities or override policy.

### Inputs

The transformation consumes canonical fields from [08_recipe_schema.md](/Users/riyer/code/kidschef/docs/08_recipe_schema.md), especially:

- `title`
- `summary`
- `ingredients`
- `steps`
- `skill_level`
- `appliances`
- `safety_flags`
- `adult_help_required`

### Transformation Rules

1. Validate that every canonical step is ordered, understandable, and safety-classified.
2. Split compound instructions into atomic guided steps.
3. Rewrite step text into plain age-appropriate language.
4. Lift adult-help requirements into visible pre-step signals.
5. Turn timers into explicit timer actions with short labels.
6. Add observable check steps where the child would otherwise need to guess.
7. Apply appliance adaptation only when it stays inside the approved safety mode and recipe contract.
8. Preserve provenance and step linkage so analytics, QA, and parent explanation can trace the child-facing flow back to the canonical record.

### Output Shape

The guided flow should preserve a mapping from each guided step to:

- source `recipe_id`
- source `step_id`
- guided step order
- simplified instruction
- adult-help status
- timer metadata
- appliance context
- success check, if added

Added guided steps are allowed when they improve clarity, but they must remain attributable to the canonical step sequence.

## Step Writing Rules

Each guided step should contain:

- one main action
- one direct object, if needed
- one visible subject such as the ingredient, tool, or appliance
- one explicit safety or help cue if relevant

Step text should usually fit in one short sentence. A second sentence is acceptable only for a brief success check or reassurance.

Examples:

- "Put the bread in the toaster."
- "Press the toast button."
- "Wait for an adult to take out the hot plate."
- "Stir until you do not see dry powder."

## Check And Confirmation Rules

Kids often need help knowing whether a step worked. The pedagogy layer should add short observable checks when useful.

- Use visual or tactile checks the child can understand.
- Prefer "looks melted," "feels cool," or "no dry spots left" over abstract quality judgments.
- Do not ask the child to assess safety-critical doneness alone if heat or undercooking risk is involved.
- If a safety-critical check is needed, require adult help rather than pushing the judgment to the child.

## Timer Teaching Rules

Timers are part of the teaching model, not just utilities.

- Start a timer only when a child can clearly identify the start condition.
- Use short timer labels tied to the action.
- When the timer ends, the next step should explain what to check.
- Do not make a child remember multiple timers at once in v1 unless the recipe is explicitly designed for it and remains simple.

## What The Pedagogy Layer Must Not Do

- weaken or remove safety labels
- infer unsafe appliance substitutions on its own
- hide blocked actions inside softer wording
- rely on free-form AI phrasing without schema-backed validation
- turn a calm educational recipe into a noisy reward loop

## Stable Contract For Other Teams

- `Kid UX` can assume every guided step is atomic and ready for one-screen presentation.
- `Safety and Policy` can assume adult-help and appliance adaptations do not override canonical risk.
- `Data and Content` can assume canonical recipe fields remain the source of truth.
- `Local AI` can generate canonical recipes or variants, but the pedagogy layer owns the child-facing rewrite.
- `Backend and Local Runtime` can persist canonical records separately from derived guided-flow render data if needed.
- `QA and Device Reliability` can test that every guided step remains traceable to source recipe data and active safety mode.

## Open Questions Kept Explicit

This guide does not resolve:

- the exact younger-age cutoff inside the 10-14 range
- whether remote AI pedagogy support exists in v1 beyond supervised fallback
- how much guided-flow state should persist across devices or reconnects

Until those decisions are made, the pedagogy layer should remain conservative, deterministic, and safety-first.
