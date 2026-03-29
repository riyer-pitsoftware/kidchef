# KidsChef Kid-Facing UX Flow Contract

## Purpose

This document defines the child-facing flow for KidsChef v1. It covers the path from meal selection through recipe completion, including suggestion review, one-step cooking, timers, safety interruptions, favorites, and the core loading and error states that must work on iPhone Safari.

The flow is designed for kids ages 10-14 using the app directly. It should feel calm, readable, and touch-friendly.

## Flow Principles

- One screen should usually have one primary action.
- The child should always know what to do next.
- Safety interruptions must be explicit and hard to miss.
- The app should use short text, large tap targets, and predictable navigation.
- The child should never need to understand backend or AI mechanics to complete a recipe.

## Core Journey

### 1. Enter

The child lands on the meal chooser or a simple home screen that leads into the meal flow.

Required actions:

- choose `breakfast`, `lunch`, `dinner`, or `snack`
- continue into ingredient entry

Required states:

- loading
- empty
- backend unavailable

### 2. Enter Ingredients

The child adds ingredients they already have.

Required behaviors:

- support search or token-style entry
- allow editing and removing ingredients
- preserve the child’s draft while moving through the flow

Required states:

- loading saved draft
- empty draft
- validation or parsing error if ingredient input cannot be understood

### 3. Apply Filters

The child selects allergy and diet filters before receiving suggestions.

Required behaviors:

- show clear filter controls
- make active filters visible
- allow the child to revise filters before searching

Required states:

- no filters selected
- some filters selected
- blocked-by-safety if the current selection would allow unsafe output

### 4. Review Suggestions

The child sees one recipe suggestion at a time or a short curated set that can be opened one at a time.

Required behaviors:

- show title, summary, and the main reason the suggestion fits
- show safety markers before the child opens the recipe
- make it easy to skip, inspect, or accept a suggestion

Required states:

- loading suggestions
- no suggestions found
- blocked-by-safety
- backend unavailable
- AI unavailable fallback to curated content

### 5. Open Recipe

The child opens a single recipe and sees the recipe detail view.

Required behaviors:

- show ingredients and steps in a calm, step-by-step format
- expose one primary action to start cooking
- keep safety markers visible

Required states:

- loading recipe detail
- recipe blocked by safety
- recipe unavailable

### 6. Cook One Step At A Time

The stepper is the main cooking experience.

Required behaviors:

- show one step at a time by default
- include `next`, `back`, and `repeat step`
- keep the current step readable on iPhone Safari
- keep timers visible while a step is active
- mark adult-help steps before the child starts them

Required states:

- current step active
- timer running
- step completed
- step blocked by safety
- step requires adult help

### 7. Finish And Save

When the recipe is complete, the child can finish the flow and optionally save the recipe as a favorite.

Required behaviors:

- confirm recipe completion
- allow favorite toggling
- provide light reward feedback without interrupting the flow
- return to meal selection or another safe next action

Required states:

- completion
- favorite saved
- favorite removed
- reward unavailable

## Screen Contracts

### Meal Selection Screen

- Primary action: choose one meal type
- Secondary actions: back, help, or restart depending on flow entry point

### Ingredient Entry Screen

- Primary action: continue with current ingredients
- Secondary actions: add ingredient, remove ingredient, edit ingredient

### Filter Screen

- Primary action: apply selected filters
- Secondary actions: clear filters, edit filters

### Suggestion Review Screen

- Primary action: open recipe
- Secondary actions: skip, refine filters, try again

### Recipe Detail Screen

- Primary action: start step flow
- Secondary actions: view ingredients, view safety markers, favorite toggle

### Stepper Screen

- Primary action: next step
- Secondary actions: back, repeat step, start timer, acknowledge adult help

### Completion Screen

- Primary action: save favorite or choose another meal
- Secondary actions: view similar recipes, return home

## State Contracts

### Loading States

Every major screen must support a loading state that:

- uses a short explanation of what is loading
- does not block the child with a blank screen
- keeps the layout stable on iPhone Safari

### Empty States

Every major screen must support an empty state that:

- explains what is missing
- tells the child how to continue
- avoids technical language

### Blocked States

Blocked states must be explicit and explain why the app cannot continue as requested.

Blocked examples:

- unsafe recipe for the selected age mode
- blocked allergen or diet conflict
- remote AI not allowed without supervision
- backend unavailable for live suggestions

The blocked state should offer the nearest safe next step, such as changing filters or trying a different meal type.

### Error States

The UI must distinguish between:

- validation error in child input
- network or backend error
- safety block
- unavailable AI

Do not merge these into one generic failure state.

## Safety Interruptions

Safety interruptions must take priority over the current step.

Required behavior:

- stop the flow when a recipe or step becomes unsafe
- explain the reason in child-friendly language
- offer a safe alternative if one exists
- show adult-help markers before any risky step begins
- do not bury safety warnings inside low-priority UI

If a step becomes unsafe after filtering, the child should not be left in a broken state. The UI should redirect to a safe alternative or a clear blocked state.

## Timers

Timers are a core part of the stepper.

Required behavior:

- show timer controls directly in the active step
- keep the timer visible while the child reads the next action
- survive brief backgrounding or page interruptions as best as the browser allows
- clearly show when a timer starts, finishes, or is unavailable

If Safari suspends timer behavior in the background, the UI must recover clearly when the app returns to the foreground.

## Favorites

Favorites are a light reward and return-path feature.

Required behavior:

- allow toggling a favorite from recipe detail or completion
- confirm the saved state visibly
- avoid turning favorites into a social or ranking system

The favorite action should be low-friction and should not interrupt the child’s recipe flow.

## iPhone Safari Rules

- Mobile layout is the default.
- Primary actions must be reachable with large taps.
- Avoid hover-only or precision-pointer assumptions.
- Keep step text short and legible without zooming.
- Do not depend on persistent background execution.
- Preserve progress when the browser can do so safely, but never treat the browser as the authoritative source of truth.

## Cross-Team Contract

- `Safety and Policy` defines which recipes and steps are blocked.
- `Recipe Pedagogy` defines how a step is simplified and when adult help is required.
- `Data and Content` defines the recipe fields this flow can render.
- `Web Platform` defines the shell, navigation, and browser behavior this flow can rely on.
- `Backend and Local Runtime` defines what data is authoritative and what can be restored.
- `Parent Dashboard and Trust` defines what child activity can be surfaced to a parent.

If the UX needs more detail than these contracts allow, that is a product decision, not a UI assumption.

