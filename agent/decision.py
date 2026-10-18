"""REUSABLE DECISION PATTERN: meal suitability policy  (#policy)

What it does
    Before the MealMind agent recommends a meal, Strands Decider 2B evaluates whether the
    candidate meal fits the user's stated constraints:
    - ingredients on hand (or close enough with a minor substitution);
    - budget limit (estimated cost vs stated maximum);
    - cooking time available;
    - dietary preferences or restrictions (vegetarian, vegan, gluten-free, halal, etc.).
    Meals that clearly fit are recommended (allow); meals that partially fit are mentioned with
    a caveat (review); meals that don't fit are skipped (block). When the decider is unsure,
    it falls back to a "review" so the user can decide themselves.

Typed questions and options
    meal_fits_ingredients (noul): can this meal be made from what the user has (or close to it)?
    meal_fits_constraints (choice): overall fit — great_fit, partial_fit, poor_fit
    dietary_safe (noul): does this meal respect the user's dietary restrictions?
    See QUESTIONS below for the full option descriptions.

Wiring
    `MealSuitabilityGuard` is called in HackathonAgent.chat() for each candidate meal before
    building the agent's recommendation list. It does not use InterventionHandler (the decision
    happens before the Strands Agent is invoked). For each candidate:
        verdict = guard.check(user_constraints, meal_description)
        if verdict == "block": skip
        if verdict == "review": include with caveat
        if verdict == "allow": recommend
    One decider call evaluates all three questions simultaneously.

How to reuse it
    Copy this file. Replace MEAL_POLICY with your domain's policy text. Reword the three
    questions and their option descriptions to match your categories. The thresholds in
    `MealSuitabilityGuard.check()` are plain `if` statements in code you own — tune them by
    running `./kit bench`.
"""

from __future__ import annotations

from typing import Any

from decider_kit import Decider

PATTERN_TAG = "#policy"

MEAL_POLICY = """A meal is suitable if:
1. It can be prepared using the ingredients the user listed (minor substitutions are acceptable).
2. Its estimated cost fits within the user's stated budget.
3. Its preparation time fits within the user's available time.
4. It respects the user's dietary restrictions (vegetarian, vegan, gluten-free, halal, etc.).
A meal is a partial fit if one constraint is marginally missed. A meal is unsuitable if it
fails dietary restrictions or misses two or more constraints clearly."""

QUESTIONS = {
    "meal_fits_ingredients": Decider.noul(
        "Can this meal be made from the ingredients the user listed, with at most one minor substitution?",
        {
            "true": "the meal's main ingredients are all present, or one minor ingredient could be substituted or skipped",
            "false": "one or more core ingredients are missing and cannot be substituted",
        },
    ),
    "meal_fits_constraints": Decider.choice(
        "How well does this meal fit the user's budget and time constraints?",
        {
            "great_fit": "both the estimated cost and preparation time clearly fit within the user's stated limits",
            "partial_fit": "one constraint (budget or time) is marginally over the limit but close enough to mention",
            "poor_fit": "both constraints are clearly exceeded, or one is far beyond the stated limit",
        },
    ),
    "dietary_safe": Decider.noul(
        "Does this meal respect the user's stated dietary restrictions (e.g. vegetarian, vegan, gluten-free, halal)?",
        {
            "true": "the meal contains no ingredients that violate the user's dietary restrictions",
            "false": "the meal contains at least one ingredient that violates the user's stated dietary restriction",
        },
    ),
}


class MealSuitabilityGuard:
    """Evaluate candidate meals against user constraints before recommending them."""

    def __init__(self, decider: Decider, block_at: float = 0.65, review_at: float = 0.35):
        self.decider = decider
        self.block_at = block_at
        self.review_at = review_at
        self.log: list[dict[str, Any]] = []

    def check(self, user_constraints: str, meal_name: str, meal_description: str) -> str:
        """Return 'allow', 'review', or 'block' for a candidate meal.

        user_constraints: plain-text summary of ingredients, budget, time, and dietary needs.
        meal_name: short name of the candidate meal.
        meal_description: ingredients, prep time, estimated cost, and any dietary tags.
        """
        state = (
            f"--- USER CONSTRAINTS ---\n{user_constraints}\n\n"
            f"--- CANDIDATE MEAL: {meal_name} ---\n{meal_description}\n\n"
            f"--- POLICY ---\n{MEAL_POLICY}"
        )
        a = self.decider.ask(state, QUESTIONS)

        fits_ingredients = a["meal_fits_ingredients"].p_yes or 0.0
        fit_label = a["meal_fits_constraints"].label or "poor_fit"
        fit_conf = a["meal_fits_constraints"].confidence or 0.0
        dietary_safe = a["dietary_safe"].p_yes or 0.0

        # Dietary restriction is hard: if unsafe, always block
        if dietary_safe < self.block_at:
            verdict = "block"
        elif fits_ingredients < self.block_at:
            verdict = "block"
        elif fit_label == "poor_fit" and fit_conf >= 0.5:
            verdict = "block"
        elif fit_label == "great_fit" and fits_ingredients >= 0.65 and dietary_safe >= 0.65:
            verdict = "allow"
        else:
            verdict = "review"

        self.log.append(
            {
                "pattern": PATTERN_TAG,
                "meal": meal_name,
                "meal_fits_ingredients": round(fits_ingredients, 3),
                "meal_fits_constraints": fit_label,
                "meal_fits_constraints_conf": round(fit_conf, 3),
                "dietary_safe": round(dietary_safe, 3),
                "verdict": verdict,
                "decider_ms": round(self.decider.last_latency_ms or 0),
            }
        )
        return verdict
