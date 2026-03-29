"""Local persistence for the KidsChef backend."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Iterable

from .contracts import RecipeRecord


class RecipeRepository:
    """Simple in-memory repository with clean replacement seams."""

    def __init__(self, recipes: Iterable[RecipeRecord] | None = None) -> None:
        self._recipes: dict[str, RecipeRecord] = {}
        source_recipes = recipes or ()
        for recipe in source_recipes:
            recipe_id = recipe["recipe_id"]
            self._recipes[recipe_id] = dict(recipe)

    def list_recipes(self) -> list[RecipeRecord]:
        return [dict(recipe) for recipe in self._recipes.values()]

    def get_recipe(self, recipe_id: str) -> RecipeRecord | None:
        recipe = self._recipes.get(recipe_id)
        if recipe is None:
            return None
        return dict(recipe)


class FavoritesStore:
    """Tiny JSON-backed favorites store for local household use."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()

    def is_favorite(self, recipe_id: str) -> bool:
        return recipe_id in self.list_favorites()

    def list_favorites(self) -> set[str]:
        with self._lock:
            if not self._path.exists():
                return set()
            try:
                payload = json.loads(self._path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return set()
            if not isinstance(payload, dict):
                return set()
            recipes = payload.get("recipe_ids")
            if not isinstance(recipes, list):
                return set()
            return {item for item in recipes if isinstance(item, str)}

    def toggle(self, recipe_id: str) -> bool:
        with self._lock:
            favorites = self.list_favorites_unlocked()
            if recipe_id in favorites:
                favorites.remove(recipe_id)
                is_favorite = False
            else:
                favorites.add(recipe_id)
                is_favorite = True
            self._write_unlocked(favorites)
            return is_favorite

    def list_favorites_unlocked(self) -> set[str]:
        if not self._path.exists():
            return set()
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return set()
        if not isinstance(payload, dict):
            return set()
        recipes = payload.get("recipe_ids")
        if not isinstance(recipes, list):
            return set()
        return {item for item in recipes if isinstance(item, str)}

    def _write_unlocked(self, recipe_ids: set[str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._path.with_suffix(".tmp")
        payload = {"recipe_ids": sorted(recipe_ids)}
        temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_path.replace(self._path)


def default_favorites_path(base_dir: Path) -> Path:
    return base_dir / "var" / "favorites.json"
