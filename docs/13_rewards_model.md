# KidsChef Rewards Model

## Purpose

This document defines the calm educational reward system for KidsChef v1. Rewards should encourage kids to complete safe recipes, try new foods, and build confidence without turning cooking into a race.

## Reward Principles

- Reward learning, not speed.
- Reward safe completion, not risky shortcuts.
- Keep rewards light and calm.
- Do not interrupt a child in the middle of cooking unless the reward is tied to a safe stopping point.
- Rewards should support the core flow, not compete with it.

## Reward Types

### Badges

Badges recognize meaningful milestones over time.

Suggested badge categories:

- first recipe completed
- first breakfast completed
- first lunch completed
- first dinner completed
- first snack completed
- try a new ingredient
- complete a recipe with adult help
- use a timer correctly
- complete a safe recipe with no safety interruptions

Rules:

- badges should be infrequent and memorable
- badges should celebrate effort and learning, not perfection
- badges should not require unsafe behavior

### Streaks

Streaks recognize consistent engagement over time.

Recommended streak themes:

- days with a completed recipe
- days with a healthy or varied meal choice
- days with a new food tried

Rules:

- streaks should count only when a safe recipe is completed or a safe food-trying action is finished
- streaks must not reset or punish the child for safety blocks, adult-help steps, or recipe unavailability
- streaks should not create pressure to cook every day

### Levels

Levels represent broad progress and confidence, not skill pressure.

Recommended level themes:

- starter
- builder
- confident helper
- food explorer

Rules:

- level progression should be slow and sparse
- levels should reflect repeated safe participation, not speed
- levels must not unlock unsafe recipes
- levels must not override age-based safety modes

### Stars For Trying Foods

Stars are the lightest reward. They should encourage food exploration and openness.

Examples:

- try a new ingredient
- try a new meal category
- finish a recipe that included a previously disliked ingredient

Rules:

- stars should be small, immediate, and optional to notice
- stars should reward trying, not finishing quickly
- stars should not appear for unsafe substitutions or blocked recipes

## Boundary Rules

Rewards must never encourage rushing or unsafe behavior.

Do not reward:

- finishing steps too quickly
- skipping safety warnings
- bypassing adult-help markers
- choosing harder or riskier appliances for extra points
- repeating unsafe actions to farm rewards
- ignoring allergies or diet filters

If a child completes a recipe with help or slower pacing, that is still a valid success.

## Placement In The Child Flow

Rewards should appear only at safe boundaries:

- after recipe completion
- after a safe recipe suggestion is accepted
- after a food is tried
- on a calm home or summary screen

Rewards should not interrupt:

- ingredient entry
- filter selection
- active recipe steps
- timer countdowns
- safety interruptions

If a reward is shown during the cooking flow, it should be brief, non-blocking, and dismissible.

## Timing Rules

- Do not show a celebratory animation that pulls attention away from the next safe action.
- Keep completion rewards short enough to preserve momentum back to the home or next recipe screen.
- If the child is in a safety block or supervised AI flow, do not introduce reward copy that could soften the seriousness of the warning.

## Copy Tone

Reward language should be calm and descriptive.

Preferred tone:

- "Nice work"
- "You finished a safe snack"
- "You tried something new"
- "Great job using the timer"

Avoid:

- hype
- pressure
- competitive ranking language
- language that implies the child should go faster

## Data And Privacy Boundaries

Reward state should stay local and minimal.

- store only what is needed to display the child’s progress
- do not create social leaderboards
- do not share rewards across households
- do not use rewards to profile the child beyond the app’s own learning context

## Cross-Team Contract

- `Kid UX` decides where rewards appear without interrupting the flow.
- `Safety and Policy` can veto any reward behavior that weakens safety.
- `Recipe Pedagogy` ensures rewards do not interfere with step clarity.
- `Parent Dashboard and Trust` may summarize reward progress at a high level, but not turn it into surveillance.
- `Backend and Local Runtime` owns the local persistence for reward progress.

If a reward idea makes the app feel busier or more competitive than calm and educational, it does not belong in v1.

