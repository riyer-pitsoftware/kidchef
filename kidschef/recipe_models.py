from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Tuple


def normalize_token(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def normalize_tokens(values: Iterable[str]) -> tuple[str, ...]:
    normalized = {normalize_token(value) for value in values if value and value.strip()}
    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class Ingredient:
    name: str
    amount: str | int | float | None = None
    unit: str | None = None
    preparation: str | None = None
    optional: bool = False
    allergen_tags: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "amount": self.amount,
            "unit": self.unit,
            "preparation": self.preparation,
            "optional": self.optional,
            "allergen_tags": list(self.allergen_tags),
        }


@dataclass(frozen=True, slots=True)
class Timer:
    label: str
    duration_seconds: int
    start_condition: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "duration_seconds": self.duration_seconds,
            "start_condition": self.start_condition,
        }


@dataclass(frozen=True, slots=True)
class Step:
    step_id: str
    order: int
    instruction: str
    safety_level: str = "safe"
    requires_adult_help: bool = False
    requires_appliance: tuple[str, ...] = ()
    timers: tuple[Timer, ...] = ()
    ingredient_refs: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "order": self.order,
            "instruction": self.instruction,
            "safety_level": self.safety_level,
            "requires_adult_help": self.requires_adult_help,
            "requires_appliance": list(self.requires_appliance),
            "timers": [timer.as_dict() for timer in self.timers],
            "ingredient_refs": list(self.ingredient_refs),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True, slots=True)
class ApplianceRequirement:
    name: str
    required: bool = True

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "required": self.required}


@dataclass(frozen=True, slots=True)
class Recipe:
    recipe_id: str
    title: str
    meal_type: str
    summary: str
    ingredients: tuple[Ingredient, ...]
    steps: tuple[Step, ...]
    servings: int | str
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty: str
    skill_level: str
    appliances: tuple[ApplianceRequirement, ...] = ()
    allergens: tuple[str, ...] = ()
    diet_tags: tuple[str, ...] = ()
    safety_flags: tuple[str, ...] = ()
    adult_help_required: bool = False
    source: str = "curated"
    validation_status: str = "validated"
    tags: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "meal_type": self.meal_type,
            "summary": self.summary,
            "ingredients": [ingredient.as_dict() for ingredient in self.ingredients],
            "steps": [step.as_dict() for step in self.steps],
            "servings": self.servings,
            "prep_time_minutes": self.prep_time_minutes,
            "cook_time_minutes": self.cook_time_minutes,
            "difficulty": self.difficulty,
            "skill_level": self.skill_level,
            "appliances": [appliance.as_dict() for appliance in self.appliances],
            "allergens": list(self.allergens),
            "diet_tags": list(self.diet_tags),
            "safety_flags": list(self.safety_flags),
            "adult_help_required": self.adult_help_required,
            "source": self.source,
            "validation_status": self.validation_status,
            "tags": list(self.tags),
        }

    @property
    def required_appliances(self) -> tuple[str, ...]:
        return tuple(
            appliance.name
            for appliance in self.appliances
            if appliance.required
        )

    @property
    def all_appliances(self) -> tuple[str, ...]:
        return tuple(appliance.name for appliance in self.appliances)

    @property
    def all_allergen_tags(self) -> tuple[str, ...]:
        ingredient_allergens = (
            tag
            for ingredient in self.ingredients
            for tag in ingredient.allergen_tags
        )
        return normalize_tokens(tuple(self.allergens) + tuple(ingredient_allergens))

    @property
    def normalized_diet_tags(self) -> tuple[str, ...]:
        return normalize_tokens(self.diet_tags)

    @property
    def normalized_safety_flags(self) -> tuple[str, ...]:
        return normalize_tokens(self.safety_flags)

    @property
    def normalized_meal_type(self) -> str:
        return normalize_token(self.meal_type)

    @property
    def normalized_validation_status(self) -> str:
        return normalize_token(self.validation_status)


@dataclass(frozen=True, slots=True)
class SafetyFilterRequest:
    meal_type: str | None = None
    blocked_allergens: tuple[str, ...] = ()
    required_diet_tags: tuple[str, ...] = ()
    blocked_diet_tags: tuple[str, ...] = ()
    available_appliances: tuple[str, ...] = ()
    safety_mode: str = "standard"
    require_validated: bool = True

    def normalized_meal_type(self) -> str | None:
        return normalize_token(self.meal_type) if self.meal_type else None

    def normalized_blocked_allergens(self) -> tuple[str, ...]:
        return normalize_tokens(self.blocked_allergens)

    def normalized_required_diet_tags(self) -> tuple[str, ...]:
        return normalize_tokens(self.required_diet_tags)

    def normalized_blocked_diet_tags(self) -> tuple[str, ...]:
        return normalize_tokens(self.blocked_diet_tags)

    def normalized_available_appliances(self) -> tuple[str, ...]:
        return normalize_tokens(self.available_appliances)

    def normalized_safety_mode(self) -> str:
        return normalize_token(self.safety_mode)


@dataclass(frozen=True, slots=True)
class FilterDecision:
    recipe: Recipe
    allowed: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "recipe_id": self.recipe.recipe_id,
            "allowed": self.allowed,
            "reasons": list(self.reasons),
            "recipe": self.recipe.as_dict(),
        }
