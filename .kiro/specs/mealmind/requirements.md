# MealMind Requirements

## Users
Students, families, and busy individuals who want practical meal suggestions from what they already have at home.

## User Stories

### Core meal planning
- WHEN a user provides their available ingredients, budget, time, and dietary restrictions, THE agent SHALL call `get_meal_suggestions` to find candidate meals.
- WHEN candidate meals are returned, THE agent SHALL ask Strands Decider 2B whether each meal fits the user's constraints BEFORE recommending it.
- THE agent SHALL recommend meals with verdict `allow` first, then `review` meals with a caveat, and SHALL NOT mention meals with verdict `block`.
- WHEN Strands Decider 2B returns confidence below 0.45 for any question, THE agent SHALL treat the meal as `review` rather than `allow`, and surface it with a note that the fit is uncertain.

### Recipe and nutrition
- WHEN a user asks for steps for a meal, THE agent SHALL call `get_recipe_steps` and present them clearly.
- WHEN a user asks about cost, THE agent SHALL call `estimate_cost` and explain what the estimate covers.
- WHEN a user asks about nutrition, THE agent SHALL call `get_nutritional_info` and highlight calories, protein, and dietary tags.

### Dietary safety
- WHEN a meal's dietary tags do not satisfy the user's stated restrictions, Strands Decider 2B SHALL return `dietary_safe = no` and the meal SHALL be blocked.
- THE agent SHALL NEVER recommend a meal that Strands Decider 2B has classified as `block`.

### Amazon Bedrock
- THE agent SHALL use Amazon Bedrock (Amazon Nova Pro by default) for all conversation and tool use, via the Strands Agents SDK.
- THE agent SHALL pass every candidate meal through Strands Decider 2B in one call per meal BEFORE the LLM response is generated.

## Acceptance Criteria (EARS)
1. WHEN the user lists ingredients, budget, time, and dietary needs, THE system SHALL return at least one meal suggestion within 15 seconds.
2. WHEN a candidate meal would violate dietary restrictions, THE system SHALL assign verdict `block` and exclude it from the reply.
3. WHEN a candidate meal partially fits constraints (one limit slightly exceeded), THE system SHALL assign verdict `review` and include a caveat in the reply.
4. WHEN all constraints are met, THE system SHALL assign verdict `allow` and recommend the meal without caveats.
5. WHEN the user requests recipe steps, cost, or nutrition for a named meal, THE system SHALL return the data from the catalogue.
