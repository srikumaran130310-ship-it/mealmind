# MealMind — AI Meal Planner

- **Pitch:** An AI meal planner that evaluates your available ingredients, budget, cooking time, and dietary preferences to recommend the most practical meal — powered by Strands Decider 2B.
- **Who it is for:** Students, families, and busy individuals who want to cook practical meals without wasting food or overspending.
- **Features:**
  - Tell the agent what ingredients you have, your budget, available time, and dietary needs — it suggests the best meal options;
  - Strands Decider 2B classifies whether each candidate meal is a great fit, a partial fit (missing an ingredient), or unsuitable — before the agent commits to a recommendation;
  - Get full recipe steps for any suggested meal;
  - Check estimated cost of a meal from your pantry;
  - View nutritional highlights for your chosen meal;
  - Deployed on Amazon Bedrock AgentCore Runtime.
- **The decision handed to Strands Decider 2B:** given the user's constraints (ingredients, budget, time, dietary needs) and a candidate meal description, is this meal a good fit (`allow`), a partial fit worth mentioning with a caveat (`review`), or unsuitable (`block`)? (`#policy`)
- **Why a decision model:** suitability depends on reading the language of constraints and meal descriptions — not simple arithmetic. A meal that "takes about 25 minutes" against a "30-minute limit" needs judgment, not an `if` statement. The decider runs once per candidate meal and returns calibrated confidence the code can act on.
- **Amazon Bedrock:** the conversation, tool use, and synthetic data generation (Amazon Nova Pro by default).
