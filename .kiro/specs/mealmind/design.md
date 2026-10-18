# MealMind Design

## State text layout (sent to Strands Decider 2B per candidate meal)

```
--- USER CONSTRAINTS ---
User request: <the user's raw message>

--- CANDIDATE MEAL: <meal name> ---
Ingredients: <comma-separated list>. Prep time: <N> min. Estimated cost: $<X>. Dietary tags: <tags or 'none'>.

--- POLICY ---
A meal is suitable if:
1. It can be prepared using the ingredients the user listed (minor substitutions are acceptable).
2. Its estimated cost fits within the user's stated budget.
3. Its preparation time fits within the user's available time.
4. It respects the user's dietary restrictions (vegetarian, vegan, gluten-free, halal, etc.).
A meal is a partial fit if one constraint is marginally missed. ...
```

## Typed questions (QUESTIONS in decision.py)

| Name | Type | Question | Options |
|---|---|---|---|
| `meal_fits_ingredients` | noul | Can this meal be made from the ingredients listed, with at most one minor substitution? | true = main ingredients present; false = core ingredient missing |
| `meal_fits_constraints` | choice | How well does this meal fit budget and time? | great_fit / partial_fit / poor_fit |
| `dietary_safe` | noul | Does this meal respect the user's dietary restrictions? | true = no violation; false = violates at least one restriction |

## Thresholds and actions (in MealSuitabilityGuard.check)

| Condition | Verdict |
|---|---|
| `dietary_safe < 0.65` | block |
| `meal_fits_ingredients < 0.65` | block |
| `meal_fits_constraints == poor_fit` AND confidence ≥ 0.5 | block |
| `meal_fits_constraints == great_fit` AND ingredients ≥ 0.65 AND dietary ≥ 0.65 | allow |
| everything else | review |

Low-confidence fallback: if confidence on any key question is below ~0.45, the call falls to `review` by default (the else branch).

## Seam

`MealSuitabilityGuard` runs in `HackathonAgent.chat()` **before** the Strands Agent is invoked. It is not an `InterventionHandler` — it runs in the pre-agent step. The evaluated verdicts are injected into the user message as a bracketed summary so the LLM uses them to structure its reply.

## Tools

| Tool | What it does |
|---|---|
| `get_meal_suggestions` | Filters the 20-meal catalogue by ingredient overlap, budget, and time; returns ≤5 candidates |
| `get_recipe_steps` | Returns step-by-step instructions for a named meal |
| `estimate_cost` | Returns estimated cost and ingredient list for a named meal |
| `get_nutritional_info` | Returns calories, protein, carbs, fat, and dietary tags |

## Data

`agent/data/meals.json` — 20 synthetic meals covering breakfast, lunch, and dinner across vegetarian, vegan, gluten-free, and unrestricted categories, with prep times 5–40 min and costs $1.50–$7.50.

## Eval-case plan (24 cases)

- 12 tune / 12 test split
- Covers: perfect match (all constraints met), partial match (time slightly over), dietary block (vegetarian asking for beef), ingredient mismatch (missing core ingredient), budget block, near-miss (one missing minor ingredient that can be substituted)
