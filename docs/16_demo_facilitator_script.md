# KidsChef Demo Facilitator Script

## Purpose

Use this script to walk a child and parent through the KidsChef MVP in a calm, repeatable way.

## Opening

Say:

- "This is KidsChef. It helps a kid pick a meal idea, add ingredients they already have, and cook one step at a time."
- "I’m going to show the child flow first, then a parent view of safety and trust."

Watch for:

- whether the introduction is too long
- whether the child understands what the app is for immediately

## Child Walkthrough

### 1. Meal Selection

Say:

- "Pick the meal you want."

Do:

- choose breakfast, lunch, dinner, or snack

Watch for:

- whether the choices are visually obvious
- whether one choice stands out without pressure

### 2. Ingredient Entry

Say:

- "Add a couple ingredients you already have."

Do:

- enter two or three ingredients
- remove one ingredient

Watch for:

- whether the input format feels easy
- whether ingredient chips are clear and editable

### 3. Filters

Say:

- "Pick the filters that matter, like allergies or diet needs."

Do:

- select one or two filters

Watch for:

- whether the filters feel understandable to a child
- whether the labels are too technical

### 4. Suggestion Review

Say:

- "Now the app shows safe recipe ideas one at a time."

Do:

- open one suggestion
- save or skip a suggestion

Watch for:

- whether the app explains why the recipe fits
- whether safety markers are visible early enough

### 5. Recipe Detail

Say:

- "Here are the ingredients and steps for this recipe."

Do:

- open the recipe detail view
- point out the ingredients list, steps, and favorite button

Watch for:

- whether the layout is readable on a phone
- whether the recipe feels calm and not crowded

### 6. One-Step Flow

Say:

- "This is the stepper. It shows one step at a time."

Do:

- start the stepper
- move next
- go back
- repeat a step
- start a timer if present

Watch for:

- whether the step text is short enough
- whether the timer stays visible
- whether the back and repeat controls are easy to find

### 7. Favorites

Say:

- "You can save a recipe you liked."

Do:

- toggle favorite on the detail screen or completion screen

Watch for:

- whether the favorite action feels lightweight
- whether it distracts from the cooking flow

## Blocked Safety Case

Say:

- "Now I’m going to show a recipe that is not safe for this mode."

Do:

- open a blocked recipe or a recipe with a blocked step
- show the blocked message

Watch for:

- whether the safety reason is clear
- whether the app points to a safe next step
- whether the warning appears before the child can continue

## Fallback Handling

### Backend Unavailable

Say:

- "Now I’ll stop the backend to show the fallback behavior."

Do:

- stop the local server
- refresh the browser
- show the degraded or unavailable state

Watch for:

- whether the app says the backend is unavailable
- whether it avoids pretending live data is current

### Ollama Or Local AI Unavailable

Say:

- "Now I’ll show what happens if local AI is unavailable."

Do:

- leave curated recipes available
- confirm the app falls back safely or labels AI suggestions as unavailable

Watch for:

- whether the demo can continue with curated content
- whether the fallback is clearly labeled

## Parent Walkthrough

Say:

- "The parent view is for safety, trust, and local controls."

Point out:

- household safety mode
- local-only analytics
- supervised remote-AI handling
- privacy-visible controls for retained data

Watch for:

- whether the parent understands what is visible
- whether the privacy story is concise and credible

## Closing Questions

Ask:

- "Which screen felt easiest?"
- "Where did you hesitate?"
- "Was anything unsafe or confusing?"
- "Did the safety warning make sense?"
- "Did the timer and favorite behavior feel calm?"
- "Would you trust this on a phone in the kitchen?"

## Observation Notes To Capture

Write down:

- first confusion point
- first moment the child smiled or engaged
- any misread button labels
- any safety concern
- any moment the parent interrupted to ask a question
- any fallback or recovery issue
- any request for a different flow or shortcut

