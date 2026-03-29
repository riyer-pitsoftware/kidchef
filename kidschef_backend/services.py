"""Business logic for recipe suggestions and favorites."""

from __future__ import annotations

from typing import Any

from kidschef import SafetyFilterRequest, filter_recipes_with_reasons, normalize_token

from .ollama import OllamaRecipeGenerator, annotate_ai_assistance
from .contracts import RecipeFilter, RecipeRecord, SuggestRequest
from .repository import FavoritesStore, RecipeRepository


class RecipeService:
    """Service boundary for recipe queries and favorite state."""

    def __init__(
        self,
        repository: RecipeRepository,
        favorites: FavoritesStore,
        recipe_filter: RecipeFilter | None = None,
        ai_generator: OllamaRecipeGenerator | None = None,
    ) -> None:
        self._repository = repository
        self._favorites = favorites
        self._recipe_filter = recipe_filter or default_recipe_filter
        self._ai_generator = ai_generator or OllamaRecipeGenerator()
        self._generated_recipes: dict[str, RecipeRecord] = {}

    def health_payload(self) -> dict[str, Any]:
        return {"ok": True, "service": "kidschef-backend", "version": "0.1.0"}

    def bootstrap_payload(self) -> dict[str, Any]:
        favorites = sorted(self._favorites.list_favorites())
        return {
            "recipes": [],
            "favorites": favorites,
            "safetyMode": "standard",
        }

    def suggest(self, request: SuggestRequest) -> dict[str, Any]:
        generation = self._ai_generator.generate(request)
        generated = [self._with_favorite(recipe) for recipe in generation.recipes]
        allowed = self._apply_rule_validation(request, generated)
        prepared = self._prepare_ranked_results(allowed, request)
        limited = prepared[: request.limit]
        limited = annotate_ai_assistance(limited, generation)
        self._generated_recipes = {recipe["recipe_id"]: dict(recipe) for recipe in limited}
        return {
            "recipes": limited,
            "count": len(limited),
            "safety_mode": request.safety_mode,
            "ai_assistance": generation.as_payload(),
        }

    def get_recipe(self, recipe_id: str) -> dict[str, Any] | None:
        generated = self._generated_recipes.get(recipe_id)
        if generated is not None:
            if generated.get("summary_only"):
                expanded = self._ai_generator.expand_recipe(generated)
                if expanded is not None:
                    expanded = self._with_favorite(expanded)
                    self._generated_recipes[recipe_id] = dict(expanded)
                    return {"recipe": expanded}
            return {"recipe": self._with_favorite(generated)}
        recipe = self._repository.get_recipe(recipe_id)
        if recipe is None:
            return None
        return {"recipe": self._with_favorite(recipe)}

    def toggle_favorite(self, recipe_id: str) -> dict[str, Any] | None:
        generated = self._generated_recipes.get(recipe_id)
        if generated is not None:
            is_favorite = self._favorites.toggle(recipe_id)
            return {
                "recipe_id": recipe_id,
                "favorite": is_favorite,
                "recipe": self._with_favorite(generated),
                "favorites": sorted(self._favorites.list_favorites()),
            }
        recipe = self._repository.get_recipe(recipe_id)
        if recipe is None:
            return None
        is_favorite = self._favorites.toggle(recipe_id)
        return {
            "recipe_id": recipe_id,
            "favorite": is_favorite,
            "recipe": self._with_favorite(recipe),
            "favorites": sorted(self._favorites.list_favorites()),
        }

    def _with_favorite(self, recipe: RecipeRecord) -> RecipeRecord:
        enriched = dict(recipe)
        enriched["favorite"] = self._favorites.is_favorite(recipe["recipe_id"])
        return enriched

    def _apply_rule_validation(self, request: SuggestRequest, recipes: list[RecipeRecord]) -> list[RecipeRecord]:
        filter_request = SafetyFilterRequest(
            meal_type=request.meal_type,
            blocked_allergens=tuple(request.allergens),
            required_diet_tags=tuple(request.diet_tags),
            available_appliances=tuple(request.appliances),
            safety_mode=request.safety_mode,
        )
        decisions = filter_recipes_with_reasons(
            tuple(_recipe_record_to_model_input(recipe) for recipe in recipes),
            filter_request,
        )
        allowed_ids = {decision.recipe.recipe_id for decision in decisions if decision.allowed}
        return [recipe for recipe in recipes if recipe["recipe_id"] in allowed_ids]

    def _prepare_ranked_results(
        self,
        recipes: list[RecipeRecord],
        request: SuggestRequest,
    ) -> list[RecipeRecord]:
        results: list[RecipeRecord] = []
        for recipe in recipes:
            prepared = self._annotate_recipe_availability(recipe, request)
            results.append(prepared)
        return results

    def _annotate_recipe_availability(
        self,
        recipe: RecipeRecord,
        request: SuggestRequest,
    ) -> RecipeRecord:
        enriched = dict(recipe)
        missing_ingredients = _missing_ingredients(recipe, request.ingredients)
        pantry_allowed = not request.ingredients or not missing_ingredients
        if pantry_allowed:
            enriched["availabilityState"] = "ready"
            enriched["missingIngredients"] = []
            enriched["possibleReason"] = ""
        else:
            enriched["availabilityState"] = "possible"
            enriched["missingIngredients"] = missing_ingredients
            enriched["possibleReason"] = _possible_reason(missing_ingredients)
        return enriched


def default_recipe_filter(recipe: RecipeRecord, context: dict[str, Any]) -> bool:
    meal_type = context["meal_type"]
    if meal_type and recipe.get("meal_type") != meal_type:
        return False

    blocked_allergens = context["allergens"]
    recipe_allergens = set(recipe.get("allergens", []))
    if blocked_allergens and recipe_allergens.intersection(blocked_allergens):
        return False

    required_diet_tags = context["diet_tags"]
    recipe_diet_tags = set(recipe.get("diet_tags", []))
    if required_diet_tags and not required_diet_tags.issubset(recipe_diet_tags):
        return False

    required_appliances = context["appliances"]
    recipe_appliances = set(recipe.get("appliances", []))
    if required_appliances and not recipe_appliances.issubset(required_appliances):
        return False

    safety_mode = context["safety_mode"]
    safety_flags = set(recipe.get("safety_flags", []))
    if safety_mode == "strict" and safety_flags.intersection({"knife", "stove", "oven"}):
        return False

    return recipe.get("validation_status") == "validated"


def summarize_recipe(recipe: RecipeRecord) -> dict[str, Any]:
    return {
        "recipe_id": recipe["recipe_id"],
        "title": recipe["title"],
        "meal_type": recipe["meal_type"],
        "summary": recipe["summary"],
        "skill_level": recipe["skill_level"],
        "adult_help_required": recipe["adult_help_required"],
        "safety_flags": recipe["safety_flags"],
        "favorite": recipe["favorite"],
        "source": recipe["source"],
    }


def _recipe_record_to_model_input(recipe: RecipeRecord):
    from kidschef.recipe_models import ApplianceRequirement, Ingredient, Recipe, Step, Timer

    appliances = tuple(
        ApplianceRequirement(
            name=item["name"] if isinstance(item, dict) else str(item),
            required=item.get("required", True) if isinstance(item, dict) else True,
        )
        for item in recipe.get("appliances", [])
    )
    ingredients = tuple(
        Ingredient(
            name=str(item.get("name", "")),
            amount=item.get("amount"),
            unit=item.get("unit"),
            preparation=item.get("preparation"),
            optional=bool(item.get("optional", False)),
            allergen_tags=tuple(item.get("allergen_tags", [])),
        )
        for item in recipe.get("ingredients", [])
    )
    steps = tuple(
        Step(
            step_id=str(item.get("step_id", "")),
            order=int(item.get("order", 0)),
            instruction=str(item.get("instruction", "")),
            safety_level=str(item.get("safety_level", "safe")),
            requires_adult_help=bool(item.get("requires_adult_help", False)),
            requires_appliance=tuple(item.get("requires_appliance", [])),
            timers=tuple(
                Timer(
                    label=str(timer.get("label", "")),
                    duration_seconds=int(timer.get("duration_seconds", 0)),
                    start_condition=timer.get("start_condition"),
                )
                for timer in item.get("timers", [])
            ),
            ingredient_refs=tuple(item.get("ingredient_refs", [])),
            warnings=tuple(item.get("warnings", [])),
        )
        for item in recipe.get("steps", [])
    )
    return Recipe(
        recipe_id=str(recipe["recipe_id"]),
        title=str(recipe["title"]),
        meal_type=str(recipe["meal_type"]),
        summary=str(recipe["summary"]),
        ingredients=ingredients,
        steps=steps,
        servings=recipe.get("servings", 1),
        prep_time_minutes=int(recipe.get("prep_time_minutes", 0)),
        cook_time_minutes=int(recipe.get("cook_time_minutes", 0)),
        difficulty=str(recipe.get("difficulty", "easy")),
        skill_level=str(recipe.get("skill_level", "independent_beginner")),
        appliances=appliances,
        allergens=tuple(recipe.get("allergens", [])),
        diet_tags=tuple(recipe.get("diet_tags", [])),
        safety_flags=tuple(recipe.get("safety_flags", [])),
        adult_help_required=bool(recipe.get("adult_help_required", False)),
        source=str(recipe.get("source", "curated")),
        validation_status=str(recipe.get("validation_status", "validated")),
        tags=tuple(recipe.get("tags", [])),
    )


def _ingredient_match_details(
    recipe: RecipeRecord,
    requested_ingredients: list[str],
) -> dict[str, object]:
    normalized_requested = {
        normalize_token(item)
        for item in requested_ingredients
        if item and normalize_token(item)
    }
    ingredient_names = {
        normalize_token(item.get("name", ""))
        for item in recipe.get("ingredients", [])
        if item.get("name")
    }

    if not normalized_requested:
        return {
            "matched_count": 0,
            "missing_count": len(ingredient_names),
            "coverage_ratio": 0.0,
            "has_overlap": False,
        }

    matched = ingredient_names & normalized_requested
    coverage_ratio = len(matched) / max(1, len(ingredient_names))
    missing_count = len(ingredient_names - normalized_requested)
    return {
        "matched_count": len(matched),
        "missing_count": missing_count,
        "coverage_ratio": coverage_ratio,
        "has_overlap": bool(matched),
    }


def _recipe_uses_only_requested_ingredients(
    recipe: RecipeRecord,
    requested_ingredients: list[str],
) -> bool:
    if not requested_ingredients:
        return True

    pantry = {normalize_token(item) for item in requested_ingredients if item and normalize_token(item)}
    required = {
        normalize_token(str(item.get("name", "")))
        for item in recipe.get("ingredients", [])
        if isinstance(item, dict) and not bool(item.get("optional", False)) and str(item.get("name", "")).strip()
    }
    return bool(required) and required.issubset(pantry)


def _missing_ingredients(
    recipe: RecipeRecord,
    requested_ingredients: list[str],
) -> list[str]:
    if not requested_ingredients:
        return []
    pantry = {normalize_token(item) for item in requested_ingredients if item and normalize_token(item)}
    ordered_missing: list[str] = []
    seen: set[str] = set()
    for item in recipe.get("ingredients", []):
        if not isinstance(item, dict) or bool(item.get("optional", False)):
            continue
        name = str(item.get("name", "")).strip()
        token = normalize_token(name)
        if not token or token in pantry or token in seen:
            continue
        ordered_missing.append(name.lower())
        seen.add(token)
    return ordered_missing


def _possible_reason(missing_ingredients: list[str]) -> str:
    if not missing_ingredients:
        return ""
    if len(missing_ingredients) == 1:
        return f"This could work if a parent adds {missing_ingredients[0]}."
    return f"This could work if a parent adds {', '.join(missing_ingredients)}."
