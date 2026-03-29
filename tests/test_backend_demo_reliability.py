from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from kidschef_backend.contracts import SuggestRequest
from kidschef_backend.ollama import OllamaRecipeGenerationResult
from kidschef_backend.repository import FavoritesStore, RecipeRepository
from kidschef_backend.services import RecipeService


class FakeGenerator:
    def __init__(self, result: OllamaRecipeGenerationResult) -> None:
        self.result = result

    def generate(self, request):
        return self.result


class BackendDemoReliabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        favorites_path = Path(self.temp_dir.name) / "favorites.json"
        self.service = RecipeService(
            RecipeRepository(),
            FavoritesStore(favorites_path),
            ai_generator=FakeGenerator(
                OllamaRecipeGenerationResult(
                    status="ok",
                    recipes=(
                        {
                            "recipe_id": "breakfast-microwave-egg-mug",
                            "title": "Microwave Egg Mug",
                            "meal_type": "breakfast",
                            "summary": "A quick egg breakfast that needs an adult for the hot step.",
                            "ingredients": [
                                {"name": "egg", "amount": 1, "unit": None, "optional": False, "allergen_tags": ["egg"]},
                                {"name": "milk", "amount": "2 tbsp", "unit": None, "optional": False, "allergen_tags": ["dairy"]},
                                {"name": "cheddar cheese", "amount": "2 tbsp", "unit": None, "optional": False, "allergen_tags": ["dairy"]},
                            ],
                            "steps": [
                                {"step_id": "step-1", "order": 1, "instruction": "Crack the egg into a microwave-safe mug.", "safety_level": "adult_help", "requires_adult_help": True, "requires_appliance": [], "timers": [], "ingredient_refs": [], "warnings": []},
                                {"step_id": "step-2", "order": 2, "instruction": "Ask an adult to microwave the mug for 60 seconds.", "safety_level": "adult_help", "requires_adult_help": True, "requires_appliance": ["microwave"], "timers": [{"label": "Cook egg", "duration_seconds": 60, "start_condition": "Start after the mug is ready"}], "ingredient_refs": [], "warnings": ["Use a microwave-safe mug."]},
                            ],
                            "servings": 1,
                            "prep_time_minutes": 4,
                            "cook_time_minutes": 1,
                            "difficulty": "easy",
                            "skill_level": "guided_beginner",
                            "appliances": [{"name": "microwave", "required": True}],
                            "allergens": ["egg", "dairy"],
                            "diet_tags": ["vegetarian"],
                            "safety_flags": ["heat", "microwave", "adult_help"],
                            "adult_help_required": True,
                            "source": "ollama_generated",
                            "validation_status": "validated",
                            "tags": [],
                        },
                    ),
                    note="generated for test",
                )
            ),
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_bootstrap_payload_returns_catalog_and_household_favorites(self) -> None:
        payload = self.service.bootstrap_payload()

        self.assertIn("recipes", payload)
        self.assertIn("favorites", payload)
        self.assertEqual(payload["safetyMode"], "standard")
        self.assertEqual(payload["recipes"], [])

    def test_legacy_frontend_payload_shape_is_parsed_for_suggestions(self) -> None:
        request = SuggestRequest.from_payload(
            {
                "mealType": "breakfast",
                "ingredients": ["egg", "milk", "cheddar cheese"],
                "filters": {
                    "allergens": [],
                    "diets": ["vegetarian"],
                    "appliances": ["microwave"],
                },
                "safetyMode": "standard",
            }
        )

        payload = self.service.suggest(request)
        recipe_ids = {recipe["recipe_id"] for recipe in payload["recipes"]}

        self.assertIn("breakfast-microwave-egg-mug", recipe_ids)

    def test_toggle_favorite_returns_updated_household_favorites(self) -> None:
        self.service.suggest(
            SuggestRequest(
                meal_type="breakfast",
                ingredients=["egg", "milk", "cheddar cheese"],
                appliances=["microwave"],
                safety_mode="standard",
            )
        )
        payload = self.service.toggle_favorite("breakfast-microwave-egg-mug")

        self.assertIsNotNone(payload)
        self.assertTrue(payload["favorite"])
        self.assertIn("breakfast-microwave-egg-mug", payload["favorites"])


if __name__ == "__main__":
    unittest.main()
