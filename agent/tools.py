"""MealMind tools: meal catalogue, recipe steps, cost estimates, and nutritional info.

Data lives in agent/data/meals.json (synthetic, generated offline). All tools read from it so
the demo and tests run without any network access.
"""

from __future__ import annotations

from strands import tool

from decider_kit.data import load

# Loaded once at import time; deterministic for tests.
_MEALS: list[dict] = []


def _meals() -> list[dict]:
    global _MEALS
    if not _MEALS:
        _MEALS = load("meals")
    return _MEALS


def _find(name: str) -> dict | None:
    nl = name.lower()
    for m in _meals():
        if m["name"].lower() == nl or m["id"].lower() == nl:
            return m
    # Fuzzy: first meal whose name contains the query
    for m in _meals():
        if nl in m["name"].lower():
            return m
    return None


@tool
def get_meal_suggestions(
    ingredients: str,
    budget_inr: float,
    max_prep_time_min: int,
    dietary_restrictions: str,
) -> dict:
    """Search the meal catalogue for options that match available ingredients, budget (in INR), time, and dietary needs.

    Returns up to 5 candidate meals with their key attributes.
    The caller (the agent) picks the best ones after Strands Decider evaluates each.
    """
    ing_list = [i.strip().lower() for i in ingredients.split(",") if i.strip()]
    candidates = []
    for m in _meals():
        meal_ings = [i.lower() for i in m.get("ingredients", [])]
        overlap = sum(1 for i in ing_list if any(i in mi or mi in i for mi in meal_ings))
        if overlap == 0:
            continue  # no overlap at all — skip immediately
        if m.get("estimated_cost_inr", 9999) > budget_inr * 1.3:
            continue  # clearly over budget
        if m.get("prep_time_min", 999) > max_prep_time_min * 1.3:
            continue  # clearly over time
        candidates.append(
            {
                "id": m["id"],
                "name": m["name"],
                "ingredients": m.get("ingredients", []),
                "prep_time_min": m.get("prep_time_min"),
                "estimated_cost_inr": m.get("estimated_cost_inr"),
                "estimated_cost_display": f"₹{m.get('estimated_cost_inr')}",
                "dietary_tags": m.get("dietary_tags", []),
                "ingredient_overlap": overlap,
            }
        )
    candidates.sort(key=lambda c: -c["ingredient_overlap"])
    return {"candidates": candidates[:5], "total_in_catalogue": len(_meals())}


@tool
def get_recipe_steps(meal_name: str) -> dict:
    """Return the step-by-step cooking instructions for a named meal."""
    m = _find(meal_name)
    if not m:
        return {"error": f"Meal '{meal_name}' not found in the catalogue."}
    return {
        "meal": m["name"],
        "prep_time_min": m.get("prep_time_min"),
        "steps": m.get("steps", []),
    }


@tool
def estimate_cost(meal_name: str) -> dict:
    """Return the estimated cost (in Indian Rupees) to prepare a meal from the catalogue."""
    m = _find(meal_name)
    if not m:
        return {"error": f"Meal '{meal_name}' not found in the catalogue."}
    return {
        "meal": m["name"],
        "estimated_cost_inr": m.get("estimated_cost_inr"),
        "estimated_cost_display": f"₹{m.get('estimated_cost_inr')}",
        "ingredients": m.get("ingredients", []),
        "note": "Estimate based on typical Indian supermarket prices; actual cost may vary.",
    }


@tool
def get_nutritional_info(meal_name: str) -> dict:
    """Return nutritional highlights (calories, protein, carbs, fat) for a named meal."""
    m = _find(meal_name)
    if not m:
        return {"error": f"Meal '{meal_name}' not found in the catalogue."}
    return {
        "meal": m["name"],
        "nutrition_per_serving": m.get("nutrition", {}),
        "dietary_tags": m.get("dietary_tags", []),
    }


TOOLS = [get_meal_suggestions, get_recipe_steps, estimate_cost, get_nutritional_info]
