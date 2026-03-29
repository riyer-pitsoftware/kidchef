# KidsChef QA Matrix

## Purpose

This matrix defines the minimum QA coverage for KidsChef v1. It focuses on iPhone Safari, local-network operation, degraded modes, AI fallback behavior, safety enforcement, supervised remote AI, and release gates for critical flows.

If a critical row fails, the build does not ship.

## Release Gates

The following flows are release-blocking:

- meal selection to recipe suggestion
- ingredient entry and filter application
- blocked recipe handling
- guided stepper flow
- timer behavior in Safari
- local AI fallback and unavailable states
- supervised remote-AI handling
- favorites persistence
- parent safety controls and visibility

## QA Matrix

| Area | Check | Expected Result | Block Release When |
|---|---|---|---|
| iPhone Safari | Open the app on current iPhone Safari and complete the main child flow | Layout is readable, taps are large, and navigation is stable | Primary actions are hidden, cramped, or require hover/precision input |
| iPhone Safari | Background and foreground the browser during an active timer | Timer state recovers clearly and the child can continue safely | Timer state is lost, misleading, or silently wrong |
| iPhone Safari | Rotate the device and revisit the stepper | Step content remains legible and the active action stays visible | Layout breaks, hides safety markers, or loses progress |
| Local network | Load the app from the household host over LAN | App loads without cloud dependency for core child flow | Core flow requires public internet or external identity |
| Local network | Disconnect and reconnect the client device | The app enters a clear degraded state and recovers without corrupting writes | Writes are silently lost or stale data is shown as current |
| Partial offline | Reopen previously loaded content after temporary host loss | Cached shell and last-viewed content remain usable where allowed | The app pretends live suggestions are available or invents new results |
| Partial offline | Start a new recommendation while the host is unavailable | The UI explains that live suggestions are unavailable | New recommendations are fabricated from stale or unsafe data |
| AI fallback | Use curated recipes when local AI is unavailable | The app serves curated or previously validated content only | The app blocks the child with no safe fallback when curated content exists |
| AI fallback | Request ingredient-based suggestions with local AI disabled | The response is `unavailable` or a safe curated fallback | Unstructured or unsafely generated content reaches the child |
| Safety policy | Select a recipe with a blocked allergen or unsafe appliance for the active mode | The recipe is blocked or safely downgraded before display | Unsafe content is shown as a valid option |
| Safety policy | Open a step marked `adult_help` or `blocked` | The child sees the warning before the action and cannot proceed unsafely | Adult-help markers are hidden, delayed, or downgraded |
| Safety policy | Verify `strict` mode with knife, stove, or oven content | The recipe is blocked or rewritten into safe alternatives only | Knife, stove, or oven actions are presented as child-only steps |
| Supervised remote AI | Trigger a remote-AI-required request without parent supervision | The request is blocked and clearly labeled as supervised-only | Remote AI proceeds without supervision or hidden approval |
| Supervised remote AI | Approve a supervised remote-AI request | The result still passes safety policy and schema validation | Remote AI bypasses policy or exposes raw model output |
| Stepper flow | Move through next, back, and repeat-step actions | Progress is preserved and the active step stays clear | Navigation loses state or skips safety markers |
| Timers | Start, finish, and recover a step timer | Timer controls remain visible and the next step is clear | Timer state disappears or becomes ambiguous |
| Favorites | Toggle a favorite from detail and completion screens | Favorite state persists according to the backend contract | Favorite actions fail silently or contradict stored state |
| Parent controls | Review household safety mode and remote-AI supervision settings | Controls are visible, local, and confirmable | Parent settings are hidden, unsafe, or unvalidated |

## Minimal Test Coverage By Critical Flow

- Meal selection: child can choose a meal type and advance.
- Ingredient entry: child can add, remove, and preserve ingredients.
- Filter application: allergy and diet filters are visible and enforced.
- Suggestion review: blocked, unavailable, and fallback states are distinct.
- Recipe detail: ingredients, steps, safety markers, and adult-help cues render correctly.
- Stepper: one-step-at-a-time progression works with back, repeat, and next.
- Timer: timer starts, counts, and recovers after brief interruption.
- Safety: blocked recipes never appear as valid child options.
- Remote AI: supervised-only paths are enforced.
- Favorites: saved state survives reload according to the backend contract.

## QA Rules

- Test against the canonical recipe schema and safety policy, not free-form text.
- Treat any ambiguous safety outcome as a failure.
- Prefer deterministic fixture data over model-dependent behavior for regression coverage.
- Verify the same scenario in at least one degraded mode and one normal mode.
- Log all safety-related failures with the owning contract and the observed state.

## Exit Criteria

KidsChef v1 is ready for release only when:

- all release-blocking flows pass on iPhone Safari
- local-network operation works without public cloud dependency for the core flow
- partial offline behavior is clear and safe
- AI fallback never shows unsafe or unvalidated output
- safety blocks and adult-help markers are explicit
- supervised remote AI cannot run without parent supervision

## Ownership

QA and Device Reliability owns this matrix and uses it to gate release readiness.
