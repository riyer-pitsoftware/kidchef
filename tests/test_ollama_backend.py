from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from kidschef_backend.contracts import SuggestRequest
from kidschef_backend.ollama import OllamaRecipeGenerationResult, _normalize_expanded_recipe
from kidschef_backend.repository import FavoritesStore, RecipeRepository
from kidschef_backend.services import RecipeService


class FakeGenerator:
    def __init__(self, result: OllamaRecipeGenerationResult) -> None:
        self.result = result
        self.calls = 0

    def generate(self, request):
        self.calls += 1
        return self.result


class OllamaSeamTests(unittest.TestCase):
    def test_service_returns_no_recipes_when_ollama_is_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = RecipeService(
                RecipeRepository(),
                FavoritesStore(Path(tmp_dir) / "favorites.json"),
            )

            response = service.suggest(SuggestRequest(meal_type="breakfast"))

        self.assertIn("recipes", response)
        self.assertEqual(response["ai_assistance"]["status"], "disabled")
        self.assertFalse(response["ai_assistance"]["used"])
        self.assertEqual(response["recipes"], [])

    def test_service_uses_generated_recipe_order_when_available(self) -> None:
        generator = FakeGenerator(
            OllamaRecipeGenerationResult(
                status="ok",
                recipes=(
                    {
                        "recipe_id": "snack-microwave-mug-cake",
                        "title": "Microwave Mug Cake",
                        "meal_type": "snack",
                        "summary": "A warm snack with a short microwave step.",
                        "ingredients": [{"name": "flour", "amount": "1/4 cup", "unit": None, "optional": False, "allergen_tags": ["wheat"]}],
                        "steps": [{"step_id": "step-1", "order": 1, "instruction": "Mix and microwave.", "safety_level": "adult_help", "requires_adult_help": True, "requires_appliance": ["microwave"], "timers": [], "ingredient_refs": [], "warnings": []}],
                        "servings": 1,
                        "prep_time_minutes": 4,
                        "cook_time_minutes": 1,
                        "difficulty": "easy",
                        "skill_level": "guided_beginner",
                        "appliances": [{"name": "microwave", "required": True}],
                        "allergens": ["wheat"],
                        "diet_tags": ["vegetarian"],
                        "safety_flags": ["adult_help", "microwave"],
                        "adult_help_required": True,
                        "source": "ollama_generated",
                        "validation_status": "validated",
                        "tags": [],
                    },
                    {
                        "recipe_id": "breakfast-berry-yogurt-parfait",
                        "title": "Berry Yogurt Parfait",
                        "meal_type": "breakfast",
                        "summary": "Simple, calm, and no-cook.",
                        "ingredients": [{"name": "yogurt", "amount": "1 cup", "unit": None, "optional": False, "allergen_tags": ["dairy"]}],
                        "steps": [{"step_id": "step-1", "order": 1, "instruction": "Layer and serve.", "safety_level": "safe", "requires_adult_help": False, "requires_appliance": [], "timers": [], "ingredient_refs": [], "warnings": []}],
                        "servings": 1,
                        "prep_time_minutes": 3,
                        "cook_time_minutes": 0,
                        "difficulty": "easy",
                        "skill_level": "independent_beginner",
                        "appliances": [],
                        "allergens": ["dairy"],
                        "diet_tags": ["vegetarian"],
                        "safety_flags": [],
                        "adult_help_required": False,
                        "source": "ollama_generated",
                        "validation_status": "validated",
                        "tags": [],
                    },
                ),
                reasons_by_recipe_id={
                    "snack-microwave-mug-cake": "Warm snack requested.",
                    "breakfast-berry-yogurt-parfait": "Simple, calm, and no-cook.",
                },
                note="generated for test",
            ),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            service = RecipeService(
                RecipeRepository(),
                FavoritesStore(Path(tmp_dir) / "favorites.json"),
                ai_generator=generator,
            )

            response = service.suggest(
                SuggestRequest(
                    ingredients=[],
                    allergens=[],
                    diet_tags=[],
                    appliances=["microwave", "toaster", "air_fryer", "stove"],
                    safety_mode="standard",
                    limit=5,
                ),
            )

        self.assertGreaterEqual(generator.calls, 1)
        self.assertEqual(response["ai_assistance"]["status"], "ok")
        self.assertEqual(
            [recipe["recipe_id"] for recipe in response["recipes"][:2]],
            ["snack-microwave-mug-cake", "breakfast-berry-yogurt-parfait"],
        )
        self.assertEqual(response["recipes"][0]["ai_reason"], "Warm snack requested.")

    def test_generated_recipe_stays_primary_even_when_ingredients_are_partial(self) -> None:
        generator = FakeGenerator(
            OllamaRecipeGenerationResult(
                status="ok",
                recipes=(
                    {
                        "recipe_id": "breakfast-microwave-egg-mug",
                        "title": "Microwave Egg Mug",
                        "meal_type": "breakfast",
                        "summary": "Warm, simple, and easy to explain step by step.",
                        "ingredients": [
                            {"name": "egg", "amount": 1, "unit": None, "optional": False, "allergen_tags": ["egg"]},
                            {"name": "milk", "amount": "2 tbsp", "unit": None, "optional": False, "allergen_tags": ["dairy"]},
                            {"name": "cheddar cheese", "amount": "2 tbsp", "unit": None, "optional": False, "allergen_tags": ["dairy"]},
                        ],
                        "steps": [{"step_id": "step-1", "order": 1, "instruction": "Crack and microwave.", "safety_level": "adult_help", "requires_adult_help": True, "requires_appliance": ["microwave"], "timers": [], "ingredient_refs": [], "warnings": []}],
                        "servings": 1,
                        "prep_time_minutes": 4,
                        "cook_time_minutes": 1,
                        "difficulty": "easy",
                        "skill_level": "guided_beginner",
                        "appliances": [{"name": "microwave", "required": True}],
                        "allergens": ["egg", "dairy"],
                        "diet_tags": ["vegetarian"],
                        "safety_flags": ["adult_help", "microwave"],
                        "adult_help_required": True,
                        "source": "ollama_generated",
                        "validation_status": "validated",
                        "tags": [],
                    },
                    {
                        "recipe_id": "breakfast-berry-yogurt-parfait",
                        "title": "Berry Yogurt Parfait",
                        "meal_type": "breakfast",
                        "summary": "A calm no-cook breakfast with yogurt, berries, and granola.",
                        "ingredients": [
                            {"name": "plain yogurt", "amount": "1 cup", "unit": None, "optional": False, "allergen_tags": ["dairy"]},
                            {"name": "berries", "amount": "1/2 cup", "unit": None, "optional": False, "allergen_tags": []},
                            {"name": "granola", "amount": "1/3 cup", "unit": None, "optional": False, "allergen_tags": ["wheat"]},
                        ],
                        "steps": [{"step_id": "step-1", "order": 1, "instruction": "Layer and serve.", "safety_level": "safe", "requires_adult_help": False, "requires_appliance": [], "timers": [], "ingredient_refs": [], "warnings": []}],
                        "servings": 1,
                        "prep_time_minutes": 5,
                        "cook_time_minutes": 0,
                        "difficulty": "easy",
                        "skill_level": "independent_beginner",
                        "appliances": [],
                        "allergens": ["dairy", "wheat"],
                        "diet_tags": ["vegetarian"],
                        "safety_flags": [],
                        "adult_help_required": False,
                        "source": "ollama_generated",
                        "validation_status": "validated",
                        "tags": [],
                    },
                ),
                reasons_by_recipe_id={
                    "breakfast-microwave-egg-mug": "Warm, simple, and easy to explain step by step.",
                },
                note="generated for test",
            ),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            service = RecipeService(
                RecipeRepository(),
                FavoritesStore(Path(tmp_dir) / "favorites.json"),
                ai_generator=generator,
            )

            response = service.suggest(
                SuggestRequest(
                    meal_type="breakfast",
                    ingredients=["plain yogurt", "berries"],
                    appliances=["microwave"],
                    safety_mode="standard",
                    limit=5,
                ),
            )

        self.assertEqual(response["recipes"][0]["recipe_id"], "breakfast-microwave-egg-mug")
        self.assertEqual(response["recipes"][0]["availabilityState"], "possible")
        self.assertEqual(response["recipes"][0]["missingIngredients"], ["egg", "milk", "cheddar cheese"])
        self.assertEqual(response["recipes"][0]["ai_reason"], "Warm, simple, and easy to explain step by step.")
        self.assertEqual(response["recipes"][1]["recipe_id"], "breakfast-berry-yogurt-parfait")

    def test_normalizer_marks_blender_recipe_as_adult_help(self) -> None:
        recipe = _normalize_expanded_recipe(
            {
                "ingredients": [
                    {"name": "banana", "amount": 1, "unit": None, "optional": False, "allergen_tags": []},
                    {"name": "milk", "amount": "1 cup", "unit": None, "optional": False, "allergen_tags": ["dairy"]},
                ],
                "steps": [
                    {
                        "step_id": "step-1",
                        "order": 1,
                        "instruction": "Blend the banana and milk until smooth.",
                        "safety_level": "safe",
                        "requires_adult_help": False,
                        "requires_appliance": ["blender"],
                        "timers": [],
                        "ingredient_refs": [],
                        "warnings": [],
                    }
                ],
                "servings": 1,
                "prep_time_minutes": 4,
                "cook_time_minutes": 0,
                "difficulty": "easy",
                "skill_level": "guided_beginner",
                "appliances": ["blender"],
                "allergens": ["dairy"],
                "diet_tags": ["vegetarian"],
                "safety_flags": [],
                "adult_help_required": False,
            },
            {
                "recipe_id": "llama-breakfast-banana-smoothie-test",
                "title": "Banana Smoothie",
                "summary": "A simple smoothie for breakfast.",
                "meal_type": "breakfast",
                "ingredients": [{"name": "banana"}, {"name": "milk"}],
                "steps": [],
                "servings": 1,
                "prep_time_minutes": 4,
                "cook_time_minutes": 0,
                "difficulty": "easy",
                "skill_level": "guided_beginner",
                "appliances": [{"name": "blender", "required": True}],
                "allergens": ["dairy"],
                "diet_tags": ["vegetarian"],
                "safety_flags": [],
                "adult_help_required": False,
                "source": "ollama_generated",
                "validation_status": "validated",
                "tags": [],
                "summary_only": True,
            },
        )

        self.assertIsNotNone(recipe)
        self.assertTrue(recipe["adult_help_required"])
        self.assertIn("adult_help", recipe["safety_flags"])
        self.assertIn("blender", recipe["safety_flags"])
        self.assertEqual(recipe["steps"][0]["safety_level"], "adult_help")


if __name__ == "__main__":
    unittest.main()
