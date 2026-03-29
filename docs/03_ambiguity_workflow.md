# KidsChef Ambiguity Triage and Decision Log

## Purpose

KidsChef will receive vague, incomplete, and conflicting requirements across product, safety, UX, AI, and platform work. This workflow defines how agents resolve those conflicts without drifting, over-scoping, or weakening safety and privacy.

## Precedence

When requirements conflict, choose the option that best satisfies this order:

1. Safety
2. Privacy
3. Core user task completion
4. Simplicity for ages 10-14
5. Technical feasibility under local-first constraints
6. Delight and gamification

If two options are otherwise equal, prefer the one that is easier to test and easier to explain to a kid or parent.

## When To Triage

Open a triage decision when any of these happen:

- A requirement is vague enough to allow multiple valid interpretations.
- Two requirements conflict.
- A feature crosses safety, UX, AI, or platform boundaries.
- A request would require new data, new persistence, or new permissions.
- AI output could change the child experience in an unsafe or unbounded way.
- A request appears to push beyond v1 scope.

## Triage Flow

1. Rewrite the request as a testable statement.
2. Identify the owning agent and any affected agents.
3. List the options that are actually on the table.
4. Rank the options against the precedence order.
5. Choose the recommended path or defer the decision if more context is required.
6. Record the decision in the log.
7. Communicate the decision to all affected agents before implementation starts.

## Decision Log Format

Every material ambiguity must be recorded in the same structure:

- `Decision`: what must be decided
- `Context`: why the question matters
- `Options`: the real alternatives
- `Recommendation`: the chosen option
- `Reasoning`: why the recommendation wins under the precedence order
- `Safety impact`: any child-safety or supervision effect
- `Privacy impact`: any data or retention effect
- `Product impact`: any user-facing effect
- `Owner`: the agent making the decision
- `Reviewers`: agents that must validate or sign off
- `Status`: `open`, `decided`, or `deferred`
- `Follow-up`: what remains unresolved, if anything

Use short entries. The log is a working artifact, not a narrative.

## Ownership Rules

- `Product Triage` owns scope, prioritization, and final product call when the issue is not safety-critical.
- `Safety and Policy` owns child safety, supervision rules, and any veto on unsafe behavior.
- `Kid UX` owns child-facing interaction choices.
- `Recipe Pedagogy` owns how steps are taught and simplified.
- `Data and Content` owns recipe schema and metadata definitions.
- `Web Platform` owns client runtime, mobile web constraints, and app shell behavior.
- `Backend and Local Runtime` owns local storage, service boundaries, and household deployment shape.
- `Local AI` owns recommendation and generation behavior within the safety policy.
- `Parent Dashboard and Trust` owns parent-visible explanations and controls.
- `Gamification` owns rewards mechanics.
- `QA and Device Reliability` owns release readiness and verification.

If ownership is unclear, `Product Triage` assigns a temporary owner before work begins.

## Escalation Rules

- Escalate to `Safety and Policy` if a choice could affect child safety, adult supervision, or restricted content.
- Escalate to `Data and Content` if the choice changes content shape, tags, or recipe metadata.
- Escalate to `Web Platform` or `Backend and Local Runtime` if the choice changes runtime behavior or storage.
- Escalate to `Local AI` if the choice changes prompts, outputs, or recommendation logic.
- Escalate to `Kid UX` if the choice changes the child-facing flow or wording.
- Escalate to `QA and Device Reliability` if the choice changes a safety-critical or device-sensitive path.

## Resolution Rules

- If the requirement is vague, convert it into a testable acceptance criterion before implementation.
- If the requirement conflicts with safety or privacy, tighten the requirement rather than relaxing the policy.
- If the requirement expands scope, defer it unless it is necessary for the current v1 flow.
- If the requirement depends on remote AI, require explicit supervision rules first.
- If the requirement needs more data than the product already collects, default to collecting less.

## Example Decision

- `Decision`: Should a recipe step be shown as one paragraph or split into two steps?
- `Options`: one paragraph, two steps
- `Recommendation`: two steps
- `Reasoning`: easier for ages 10-14, easier to test, better for timers and adult-help markers
- `Safety impact`: neutral or improved
- `Privacy impact`: none
- `Product impact`: clearer guidance
- `Owner`: `Recipe Pedagogy`
- `Reviewers`: `Kid UX`, `QA and Device Reliability`
- `Status`: `decided`
- `Follow-up`: none

## Working Rule For All Agents

No agent should begin implementation on an ambiguous requirement until:

- the ambiguity is written as a decision record,
- the owner is named,
- the precedence order has been applied,
- and the affected teams have been notified.

