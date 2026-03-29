from __future__ import annotations

from collections.abc import Iterable, Sequence

from .recipe_models import (
    FilterDecision,
    Recipe,
    SafetyFilterRequest,
    normalize_token,
    normalize_tokens,
)

STRICT_BLOCKED_FLAGS = {
    "adult_help",
    "heat",
    "knife",
    "oven",
    "sharp_tool",
    "stove",
    "hot_surface",
}

STANDARD_BLOCKED_FLAGS = {
    "knife",
    "oven",
    "sharp_tool",
    "stove",
    "hot_surface",
}


def filter_recipes(recipes: Sequence[Recipe], request: SafetyFilterRequest) -> list[Recipe]:
    return [
        decision.recipe
        for decision in filter_recipes_with_reasons(recipes, request)
        if decision.allowed
    ]


def filter_recipes_with_reasons(
    recipes: Sequence[Recipe],
    request: SafetyFilterRequest,
) -> list[FilterDecision]:
    decisions: list[FilterDecision] = []
    normalized_request = _normalized_request(request)

    for recipe in recipes:
        reasons = _recipe_rejection_reasons(recipe, normalized_request)
        decisions.append(
            FilterDecision(
                recipe=recipe,
                allowed=not reasons,
                reasons=tuple(reasons),
            )
        )

    return decisions


def _normalized_request(request: SafetyFilterRequest) -> SafetyFilterRequest:
    return SafetyFilterRequest(
        meal_type=request.normalized_meal_type(),
        blocked_allergens=request.normalized_blocked_allergens(),
        required_diet_tags=request.normalized_required_diet_tags(),
        blocked_diet_tags=request.normalized_blocked_diet_tags(),
        available_appliances=request.normalized_available_appliances(),
        safety_mode=request.normalized_safety_mode(),
        require_validated=request.require_validated,
    )


def _recipe_rejection_reasons(
    recipe: Recipe,
    request: SafetyFilterRequest,
) -> list[str]:
    reasons: list[str] = []

    if request.require_validated and recipe.normalized_validation_status != "validated":
        reasons.append(f"validation_status:{recipe.normalized_validation_status}")

    if request.meal_type and recipe.normalized_meal_type != request.meal_type:
        reasons.append("meal_type_mismatch")

    _append_blocked_tags(
        reasons,
        "blocked_allergen",
        request.blocked_allergens,
        recipe.all_allergen_tags,
    )
    _append_missing_tags(
        reasons,
        "missing_diet_tag",
        request.required_diet_tags,
        recipe.normalized_diet_tags,
    )
    _append_blocked_tags(
        reasons,
        "blocked_diet_tag",
        request.blocked_diet_tags,
        recipe.normalized_diet_tags,
    )

    _append_missing_appliances(reasons, recipe, request.available_appliances)
    _append_safety_reasons(reasons, recipe, request.safety_mode)

    return reasons


def _append_blocked_tags(
    reasons: list[str],
    label: str,
    blocked_tags: Iterable[str],
    candidate_tags: Iterable[str],
) -> None:
    blocked = set(normalize_tokens(blocked_tags))
    candidate = set(normalize_tokens(candidate_tags))
    for tag in sorted(blocked & candidate):
        reasons.append(f"{label}:{tag}")


def _append_missing_tags(
    reasons: list[str],
    label: str,
    required_tags: Iterable[str],
    candidate_tags: Iterable[str],
) -> None:
    required = set(normalize_tokens(required_tags))
    candidate = set(normalize_tokens(candidate_tags))
    for tag in sorted(required - candidate):
        reasons.append(f"{label}:{tag}")


def _append_missing_appliances(
    reasons: list[str],
    recipe: Recipe,
    available_appliances: Iterable[str],
) -> None:
    available = set(normalize_tokens(available_appliances))
    required = set(normalize_tokens(recipe.required_appliances))
    for appliance in sorted(required - available):
        reasons.append(f"missing_appliance:{appliance}")


def _append_safety_reasons(
    reasons: list[str],
    recipe: Recipe,
    safety_mode: str,
) -> None:
    mode = normalize_token(safety_mode)
    flags = set(recipe.normalized_safety_flags)
    step_levels = {normalize_token(step.safety_level) for step in recipe.steps}

    if mode == "strict":
        for flag in sorted(flags & STRICT_BLOCKED_FLAGS):
            reasons.append(f"strict_blocked_flag:{flag}")
        if recipe.adult_help_required:
            reasons.append("strict_requires_adult_help")
        if "adult_help" in step_levels:
            reasons.append("strict_adult_help_step")
        if "blocked" in step_levels:
            reasons.append("blocked_step_present")
        return

    if mode in {"standard", "supervised"}:
        if "blocked" in step_levels:
            reasons.append("blocked_step_present")
        if recipe.adult_help_required:
            return reasons
        for flag in sorted(flags & (STANDARD_BLOCKED_FLAGS | {"adult_help", "heat"})):
            reasons.append(f"blocked_flag:{flag}")
        if "adult_help" in step_levels or flags & {"adult_help", "heat"}:
            reasons.append("adult_help_missing")
        return

    reasons.append(f"unknown_safety_mode:{mode}")
