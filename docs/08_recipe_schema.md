# KidsChef Recipe Schema

## Purpose

This document defines the canonical recipe shape for KidsChef v1. It applies to curated recipes, AI-derived recipe candidates, and any recipe data other teams consume for UI, safety, backend storage, or analytics.

The schema is intentionally minimal: if a field is not listed here, other teams should not assume it exists.

## Canonical Recipe Object

Every recipe record must include:

- `recipe_id`: stable local identifier
- `title`: human-readable recipe name
- `meal_type`: one of `breakfast`, `lunch`, `dinner`, `snack`
- `summary`: short kid-facing description
- `ingredients`: ordered list of ingredient objects
- `steps`: ordered list of step objects
- `servings`: integer or small range
- `prep_time_minutes`: integer
- `cook_time_minutes`: integer
- `difficulty`: one of `easy`, `medium`, `hard`
- `skill_level`: kid-safety and cooking complexity label used for filtering
- `appliances`: list of required or optional appliances
- `allergens`: list of detected allergen tags
- `diet_tags`: list of dietary tags such as `vegetarian` or `dairy_free`
- `safety_flags`: list of safety markers
- `adult_help_required`: boolean
- `source`: `curated` or `ai_derived`
- `validation_status`: `pending`, `validated`, or `rejected`

If a recipe is missing any required field, it is not valid for child-facing use.

## Ingredient Object

Each ingredient entry must include:

- `name`: canonical ingredient name
- `amount`: optional quantity
- `unit`: optional unit
- `preparation`: optional prep note such as `chopped` or `softened`
- `optional`: boolean
- `allergen_tags`: list of ingredient-level allergen tags

Ingredient names should be normalized so safety and filtering logic can compare them deterministically.

## Step Object

Each step entry must include:

- `step_id`: stable step identifier within the recipe
- `order`: integer sequence number
- `instruction`: child-facing step text
- `safety_level`: `safe`, `adult_help`, or `blocked`
- `requires_adult_help`: boolean
- `requires_appliance`: list of appliances used by the step
- `timers`: optional list of timer objects
- `ingredient_refs`: optional list of referenced ingredient names or ids
- `warnings`: optional short safety notes

Steps must be ordered and independently understandable. Long compound steps should be split rather than packed into one paragraph.

## Timer Object

When a step needs timing, use:

- `label`: timer name shown to the child
- `duration_seconds`: integer
- `start_condition`: optional note describing when the timer starts

## Metadata Contract

### Meal Metadata

- `meal_type` is required and must be one of the supported meal categories.

### Appliance Metadata

- `appliances` must distinguish between required and optional use.
- Allowed appliance labels must be normalized, such as `microwave`, `toaster`, `air_fryer`, `stove`, `oven`.
- If a recipe requires an appliance disallowed by the active safety mode, the recipe cannot be shown in that mode.

### Skill Metadata

- `skill_level` must be coarse and stable enough for filtering.
- Skill metadata should reflect both recipe complexity and child independence.
- If a recipe is hard to simplify safely, raise the skill level or block it.

### Allergy And Diet Metadata

- `allergens` is a required list, even when empty.
- `diet_tags` is a required list, even when empty.
- Tags must be normalized to canonical values so filters can be applied deterministically.
- If any ingredient introduces an ambiguous allergen match, the recipe must fail validation until resolved.

### Safety Metadata

- `safety_flags` is a required list.
- Valid safety flags include markers such as `knife`, `heat`, `stove`, `oven`, `sharp_tool`, `hot_surface`, `adult_help`.
- `adult_help_required` must be true if any step is not safe for the active mode without adult assistance.

## AI-Derived Recipe Validation

AI-generated or AI-transformed recipes are not valid until they pass these checks:

1. The recipe must conform to the canonical object shape.
2. All required fields must be present and normalized.
3. Ingredients, appliances, allergens, and diet tags must be machine-checkable.
4. Every step must have a clear order, instruction, and safety classification.
5. No step may hide a knife, heat, stove, or oven action inside vague language.
6. The recipe must satisfy the active safety mode without relying on unstated assumptions.
7. If validation fails, the recipe is rejected rather than partially shown.

Validated AI-derived recipes may be stored locally only after passing safety and schema checks.

## Minimum Fields Other Teams Can Depend On

Other teams may assume every valid recipe has:

- `recipe_id`
- `title`
- `meal_type`
- `summary`
- `ingredients`
- `steps`
- `servings`
- `prep_time_minutes`
- `cook_time_minutes`
- `difficulty`
- `skill_level`
- `appliances`
- `allergens`
- `diet_tags`
- `safety_flags`
- `adult_help_required`
- `source`
- `validation_status`

Other teams must not depend on extra free-form text or unstructured AI output.

## Consumer Expectations

- `Kid UX` can render the title, summary, ingredients, steps, timers, and safety markers directly from this schema.
- `Safety and Policy` can block or downgrade recipes based on allergens, appliances, and safety flags.
- `Local AI` can emit candidates in this shape, but cannot skip validation.
- `Backend and Local Runtime` can persist this record as the canonical recipe unit.
- `QA and Device Reliability` can test the schema against safety modes and degraded AI behavior.

## Example Records

### Example 1: Curated Safe Snack

```json
{
  "recipe_id": "snack-apple-yogurt-dip",
  "title": "Apple Yogurt Dip",
  "meal_type": "snack",
  "summary": "Apple slices with a quick cinnamon yogurt dip.",
  "ingredients": [
    {
      "name": "apple",
      "amount": 1,
      "unit": "whole",
      "preparation": "pre-sliced",
      "optional": false,
      "allergen_tags": []
    },
    {
      "name": "plain yogurt",
      "amount": 0.5,
      "unit": "cup",
      "optional": false,
      "allergen_tags": ["dairy"]
    }
  ],
  "steps": [
    {
      "step_id": "step-1",
      "order": 1,
      "instruction": "Put the yogurt in a bowl.",
      "safety_level": "safe",
      "requires_adult_help": false,
      "requires_appliance": [],
      "timers": [],
      "ingredient_refs": ["plain yogurt"],
      "warnings": []
    },
    {
      "step_id": "step-2",
      "order": 2,
      "instruction": "Dip the apple slices into the yogurt and eat.",
      "safety_level": "safe",
      "requires_adult_help": false,
      "requires_appliance": [],
      "timers": [],
      "ingredient_refs": ["apple", "plain yogurt"],
      "warnings": []
    }
  ],
  "servings": 1,
  "prep_time_minutes": 5,
  "cook_time_minutes": 0,
  "difficulty": "easy",
  "skill_level": "independent_beginner",
  "appliances": [],
  "allergens": ["dairy"],
  "diet_tags": ["vegetarian"],
  "safety_flags": [],
  "adult_help_required": false,
  "source": "curated",
  "validation_status": "validated"
}
```

### Example 2: Standard-Mode Breakfast With Adult Help

```json
{
  "recipe_id": "breakfast-toast-egg-mug",
  "title": "Microwave Egg Toast",
  "meal_type": "breakfast",
  "summary": "A quick egg and toast breakfast with microwave help.",
  "ingredients": [
    {
      "name": "egg",
      "amount": 1,
      "unit": "whole",
      "optional": false,
      "allergen_tags": ["egg"]
    },
    {
      "name": "bread",
      "amount": 1,
      "unit": "slice",
      "optional": false,
      "allergen_tags": ["wheat"]
    }
  ],
  "steps": [
    {
      "step_id": "step-1",
      "order": 1,
      "instruction": "Crack the egg into a microwave-safe mug with an adult nearby.",
      "safety_level": "adult_help",
      "requires_adult_help": true,
      "requires_appliance": ["microwave"],
      "timers": [],
      "ingredient_refs": ["egg"],
      "warnings": ["Use a microwave-safe mug."]
    },
    {
      "step_id": "step-2",
      "order": 2,
      "instruction": "Microwave the mug for 60 seconds with adult help.",
      "safety_level": "adult_help",
      "requires_adult_help": true,
      "requires_appliance": ["microwave"],
      "timers": [
        {
          "label": "Cook egg",
          "duration_seconds": 60
        }
      ],
      "ingredient_refs": ["egg"],
      "warnings": ["The mug may be hot."]
    }
  ],
  "servings": 1,
  "prep_time_minutes": 3,
  "cook_time_minutes": 1,
  "difficulty": "easy",
  "skill_level": "guided_beginner",
  "appliances": ["microwave", "toaster"],
  "allergens": ["egg", "wheat"],
  "diet_tags": ["vegetarian"],
  "safety_flags": ["heat", "hot_surface", "adult_help"],
  "adult_help_required": true,
  "source": "curated",
  "validation_status": "validated"
}
```

## Non-Goals

- Free-form recipe blogs
- User-authored recipe publishing
- Rich nutritional tracking
- Social or sharing metadata
- Hidden model reasoning
