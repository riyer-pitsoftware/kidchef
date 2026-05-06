from __future__ import annotations

import unittest

from kidschef import SEED_RECIPES, SafetyFilterRequest, filter_recipes, filter_recipes_with_reasons


class SafetyFilteringTests(unittest.TestCase):
    def test_seed_data_covers_all_meal_types(self) -> None:
        meal_types = {recipe.meal_type for recipe in SEED_RECIPES}
        self.assertEqual(meal_types, {"breakfast", "lunch", "dinner", "snack"})

    def test_strict_mode_no_longer_blocks_adult_help_recipes(self) -> None:
        request = SafetyFilterRequest(
            meal_type="breakfast",
            available_appliances=("microwave",),
            safety_mode="strict",
        )

        allowed_ids = {recipe.recipe_id for recipe in filter_recipes(SEED_RECIPES, request)}
        self.assertIn("breakfast-berry-yogurt-parfait", allowed_ids)
        self.assertIn("breakfast-microwave-egg-mug", allowed_ids)

    def test_standard_mode_allows_adult_help_when_appliance_is_available(self) -> None:
        request = SafetyFilterRequest(
            meal_type="breakfast",
            available_appliances=("microwave",),
            safety_mode="standard",
        )

        allowed_ids = {recipe.recipe_id for recipe in filter_recipes(SEED_RECIPES, request)}
        self.assertIn("breakfast-microwave-egg-mug", allowed_ids)

    def test_allergen_filter_blocks_matching_recipe(self) -> None:
        request = SafetyFilterRequest(
            meal_type="snack",
            blocked_allergens=("dairy",),
            safety_mode="standard",
        )

        allowed_ids = {recipe.recipe_id for recipe in filter_recipes(SEED_RECIPES, request)}
        self.assertNotIn("snack-apple-yogurt-dip", allowed_ids)

    def test_missing_required_appliance_blocks_recipe(self) -> None:
        request = SafetyFilterRequest(
            meal_type="lunch",
            safety_mode="standard",
            available_appliances=(),
        )

        decisions = filter_recipes_with_reasons(SEED_RECIPES, request)
        lunch_ids = {
            decision.recipe.recipe_id
            for decision in decisions
            if decision.allowed
        }

        self.assertIn("lunch-hummus-veggie-wrap", lunch_ids)
        self.assertNotIn("lunch-air-fryer-pita-pizza", lunch_ids)


if __name__ == "__main__":
    unittest.main()
