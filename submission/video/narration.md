0. MealMind is an AI meal planner that runs on Amazon Bedrock. Before recommending any meal, it uses Strands Decider to check whether the meal actually fits your ingredients, budget, time, and dietary needs.

1. Tell MealMind what you have, your budget and time — it picks the best meal and explains why. What it does: Ask for meals by ingredients, budget in rupees, time, and dietary needs. Strands Decider evaluates every candidate meal before it is recommended. Partial fits are shown with a caveat; unsuitable meals are silently skipped. Get full recipe steps, cost breakdown, or nutrition info for any suggestion.

2. The user lists what they have. The Decider evaluates each candidate meal before any recommendation is made. The decider scored meal fits ingredients 0.70, meal fits constraints conf 0.73, dietary safe 0.79, so the verdict was allow, in 4.3 seconds. The decider scored meal fits ingredients 0.57, meal fits constraints conf 0.66, dietary safe 0.36, so the verdict was block, in 3.6 seconds.

3. The user asks for the recipe. No decision is needed here — this is a straightforward lookup. No decision was needed on this turn.

4. A simpler request — fewer ingredients, tight budget. The Decider checks what fits. The decider scored meal fits ingredients 0.65, meal fits constraints conf 0.72, dietary safe 0.77, so the verdict was allow, in 3.6 seconds. The decider scored meal fits ingredients 0.53, meal fits constraints conf 0.59, dietary safe 0.60, so the verdict was block, in 3.6 seconds.

5. The user asks about nutrition and dietary info for their chosen meal. The decider scored meal fits ingredients 0.60, meal fits constraints conf 0.56, dietary safe 0.48, so the verdict was block, in 3.5 seconds. The decider scored meal fits ingredients 0.44, meal fits constraints conf 0.41, dietary safe 0.34, so the verdict was block, in 3.8 seconds.

6. On 24 labelled decisions, with the decider running locally on this machine, Strands Decider was 79% accurate at a median of 295 milliseconds, against 96% and 1276 milliseconds for the Bedrock LLM asked the same questions.

7. One forward pass per candidate meal. Typed answers with calibrated confidence. The Decider blocks unsuitable meals before the LLM ever sees them — saving tokens, time, and bad recommendations.