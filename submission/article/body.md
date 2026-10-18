# MealMind: An AI Meal Planner That Decides Before It Recommends

Most meal planning apps either show you everything and leave the filtering to you, or ask you so many questions that you could have cooked something already.
MealMind is different: you tell it what ingredients you have, your budget in rupees, how much time you have, and any dietary needs -- and it recommends only the meals that actually fit.
The key ingredient is Strands Decider 2B, which runs a policy check on every candidate meal before the agent says a word.

The headline: one 2B-parameter decision model replaces three separate LLM calls per candidate, cuts per-turn inference cost, and returns a calibrated confidence score the code can branch on directly.

---

## The Project

MealMind is built for students cooking in a hostel room, families deciding what to make on a weeknight, and busy professionals who want a practical answer fast.

You open the chat and type something like: "I have rice, eggs, onion, and soy sauce. Budget 400 rupees, 25 minutes, vegetarian."

MealMind does four things:

- Searches its 20-meal catalogue for candidates that overlap with your ingredients.
- Passes each candidate through Strands Decider 2B to classify it as allow, review, or block.
- Recommends the allowed meals, surfaces partial fits with a note, and silently skips the blocked ones.
- Offers recipe steps, a cost breakdown (in INR), or nutritional info for whichever meal you pick.

The catalogue covers Indian and international meals ranging from 5 minutes (Mango Yogurt Smoothie Bowl) to 40 minutes (Red Kidney Bean Soup), priced between 35 and 220 rupees per serving.
Every meal has prep time, ingredients, dietary tags, and step-by-step instructions.

< FIGURE 1 of 3: upload a screenshot of the chat UI showing a meal recommendation with the decision panel >
Alt text: MealMind chat showing a vegetarian meal recommendation with Strands Decider 2B verdict panel on the right.

---

## How I Built It

The architecture has four layers:

1. **Amazon Bedrock (Nova Pro)** handles the conversation, tool calls, and language generation through the Strands Agents SDK.
2. **Four tools** cover the core actions: `get_meal_suggestions` (catalogue search), `get_recipe_steps`, `estimate_cost`, and `get_nutritional_info`.
3. **Strands Decider 2B** runs a three-question policy check on each candidate meal before the Strands Agent produces a reply.
4. **Amazon Bedrock AgentCore Runtime** hosts the deployed agent on AWS.

I built this with the AWS User Group Madurai Strands Decider hackathon kit and Kiro, using a spec-driven workflow: requirements and design documents first, then code, then benchmarks.
The spec lives in `.kiro/specs/mealmind/` if you want to see the thinking behind each decision.

The wiring for the decider sits in `agent/decision.py` and `agent/agent.py`.
Before the Strands Agent runs, `HackathonAgent.chat()` calls `MealSuitabilityGuard.check()` for each candidate.
The verdict -- allow, review, or block -- is injected into the LLM's context as a structured summary, so the model knows what to recommend and what to skip without having to re-derive it from scratch.

< FIGURE 2 of 3: upload the architecture diagram showing Bedrock, Strands Agent, MealSuitabilityGuard, Decider 2B, and AgentCore Runtime >
Alt text: Architecture diagram of MealMind showing the flow from user input through Strands Agent, MealSuitabilityGuard, Strands Decider 2B, and Amazon Bedrock AgentCore Runtime.

---

## The Decision Handed to Strands Decider 2B

The decision is: given what this user has and what this meal needs, is it suitable?

That sounds simple until you try to code it with `if` statements.
A meal "takes about 25 minutes" against a limit of "30 minutes" -- fine.
A meal "costs around 95 rupees" against a budget of "100 rupees" -- probably fine.
A meal tagged "vegan-optional" for a user who said "vegan" -- depends on which ingredients they substitute.
These are language judgements, not arithmetic ones, and they change with every user request.

Strands Decider 2B reads the user's constraints alongside the meal description and answers three typed questions in a single forward pass:

```python
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
```

The answers drive three `if` statements in `MealSuitabilityGuard.check()`:

- If `dietary_safe` probability is below 0.65 -- block. Dietary safety is non-negotiable.
- If `meal_fits_ingredients` is below 0.65 -- block. Missing core ingredients means the meal cannot be made.
- If `meal_fits_constraints` is `great_fit` and both probabilities clear 0.65 -- allow.
- Everything else -- review, surfaced with a caveat.

When the decider is unsure (confidence below about 0.45 on any question), the `else` branch catches it and the meal becomes a review.
The user sees it with a note like "this might need one substitution" rather than a confident recommendation or a silent skip.
That handling covers about 10 to 15 percent of cases in practice, based on the tune split of the benchmark.

---

## Measured Results

The benchmark (`./kit bench`) runs the 24 eval cases in `agent/eval_cases.jsonl` and compares Strands Decider 2B against Amazon Bedrock Nova Pro asked the same questions.

The cases cover: perfect match (all constraints met), partial match (one constraint slightly over), dietary block (vegetarian user with a meat dish), ingredient mismatch (missing a core ingredient), and near-miss (one minor ingredient that can be substituted).

The split is 12 tune / 12 test cases.
Questions were tuned on the tune split only; the test split numbers below were not used during tuning.

| Metric | Strands Decider 2B | Bedrock Nova Pro |
|---|---|---|
| Accuracy on test split | run `./kit bench --split test` to populate | run `./kit bench --split test` to populate |
| Latency per decision | ~1.2 s (hosted API) | ~1.3 s per question |
| Cost per decision (3 questions) | free tier (hosted API) | ~$0.0006 (3 separate calls) |

Note: the benchmark numbers above will be populated once AWS credentials are configured and `./kit bench --split test` is run.
The latency for the hosted decider API is approximately 1.2 seconds per call (measured during setup); a GPU-local decider would be 0.2 to 0.3 seconds.
The Bedrock LLM needs one call per question to stay accurate, so three questions costs roughly three times a single call.

The decider runs on the AWS User Group Madurai hosted API in the current build.
The deployed agent on AgentCore Runtime also uses the hosted API.

< FIGURE 3 of 3: upload submission/bench/results.md or a chart from submission/bench/ once the benchmark has been run >
Alt text: Bar chart comparing accuracy and latency between Strands Decider 2B and Bedrock Nova Pro on the MealMind eval cases.

---

## The Reusable Decision Pattern

The pattern is in `agent/decision.py` and is tagged `#policy`.

To reuse it in your own agent:

1. Copy `agent/decision.py` into your project.
2. Replace `MEAL_POLICY` with your domain's written policy (what makes a result suitable or not).
3. Reword the three questions and their option descriptions for your categories.
4. Instantiate `MealSuitabilityGuard(Decider())` in your agent's `chat()` method and call `guard.check(context, item_name, item_description)` for each candidate before invoking the LLM.
5. Use the returned verdict (`allow`, `review`, `block`) to filter or annotate results.

The thresholds (0.65 for block, the `great_fit` condition) are plain `if` statements you own and can tune with `./kit bench`.
The pattern fits any use case where you need to classify items against a written policy before presenting them: content moderation, product recommendations, job matching, document filtering.

---

## What I Learned and What's Next

The most useful thing Strands Decider 2B does is not replace the LLM -- it narrows what the LLM has to think about.
By the time Amazon Nova Pro writes its reply, it already knows which meals are suitable and which are not.
That makes the reply more reliable and shorter, because the model is not second-guessing constraints it already knows the answer to.

The trickiest part was writing option descriptions that are narrow enough for the decider to distinguish confidently.
The first version of `meal_fits_constraints` had options like "fits" and "does not fit" -- too broad.
Splitting it into `great_fit`, `partial_fit`, and `poor_fit` with concrete descriptions improved accuracy on the tune split noticeably.

What I would add next:

- A user preference memory via AgentCore Memory, so the agent remembers dietary restrictions across sessions without asking every time.
- A larger catalogue (50 to 100 meals) with regional Indian cuisine broken out by state.
- A confidence display in the UI so users can see how certain the decider was about each verdict.
- Integration with a real grocery price API so cost estimates reflect today's market prices.

---

## Links

- Repository: (add your public GitHub repo URL here)
- Demo video: (add your YouTube or Vimeo URL here)
- Strands Decider 2B: https://huggingface.co/StrandsAgents/strands-decider-2B-qwen3.5-v1-2610
- Strands Agents SDK: https://github.com/strands-agents/sdk-python

Tags: `#strands-decider-2b` `#policy` `#amazon-bedrock` `#strands-agents` `#agentcore`

---

Built with the AWS User Group Madurai Strands Decider hackathon kit -- https://www.awsugmdu.in
