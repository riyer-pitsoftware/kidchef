"""Shared backend contracts for the KidsChef local server."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


RecipeRecord = dict[str, Any]
RecipeFilter = Callable[[RecipeRecord, dict[str, Any]], bool]


@dataclass(slots=True)
class SuggestRequest:
    """Structured request passed into recipe suggestion logic."""

    meal_type: str | None = None
    ingredients: list[str] = field(default_factory=list)
    allergens: list[str] = field(default_factory=list)
    diet_tags: list[str] = field(default_factory=list)
    appliances: list[str] = field(default_factory=list)
    safety_mode: str = "strict"
    limit: int = 5

    @classmethod
    def from_payload(cls, payload: dict[str, Any] | None) -> "SuggestRequest":
        payload = payload or {}
        filters = payload.get("filters")
        filters = filters if isinstance(filters, dict) else {}
        return cls(
            meal_type=_as_optional_string(payload.get("meal_type") or payload.get("mealType")),
            ingredients=_normalize_ingredients(payload.get("ingredients")),
            allergens=_normalize_string_list(payload.get("allergens") or filters.get("allergens")),
            diet_tags=_normalize_string_list(payload.get("diet_tags") or payload.get("dietTags") or filters.get("diets")),
            appliances=_normalize_string_list(payload.get("appliances") or filters.get("appliances")),
            safety_mode=_as_optional_string(payload.get("safety_mode") or payload.get("safetyMode")) or "strict",
            limit=_coerce_limit(payload.get("limit")),
        )

    def as_context(self) -> dict[str, Any]:
        return {
            "meal_type": self.meal_type,
            "ingredients": set(self.ingredients),
            "allergens": set(self.allergens),
            "diet_tags": set(self.diet_tags),
            "appliances": set(self.appliances),
            "safety_mode": self.safety_mode,
            "limit": self.limit,
        }


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            cleaned = item.strip().lower()
            if cleaned:
                result.append(cleaned)
    return result


def _normalize_ingredients(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            cleaned = item.strip().lower()
            if cleaned:
                result.append(cleaned)
    return result


def _as_optional_string(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned:
            return cleaned
    return None


def _coerce_limit(value: Any) -> int:
    if isinstance(value, bool):
        return 5
    if isinstance(value, int):
        return max(1, min(value, 20))
    return 5
