"""MealMind: an AI meal planner that recommends practical meals from what you have.

Strands Decider 2B evaluates each candidate meal against the user's constraints (ingredients,
budget, time, dietary needs) *before* the agent commits to a recommendation. Amazon Bedrock
(Nova Pro by default) handles the conversation and tool use.

    from agent.agent import HackathonAgent
    out = HackathonAgent().chat("I have rice, eggs, and onion. Budget ₹400, 20 min, vegetarian.")
    out["reply"], out["decisions"]
"""

from __future__ import annotations

import time
from typing import Any

from strands import Agent

from decider_kit import Decider
from decider_kit.llm import agent_model, default_model_id, strip_thinking

from .decision import MealSuitabilityGuard, QUESTIONS
from .tools import TOOLS, _meals

NAME = "MealMind — AI Meal Planner"

SYSTEM_PROMPT = """You are MealMind, a friendly AI meal planner for students, families, and busy individuals.

Your job:
1. Ask the user (if not already stated) for: available ingredients, budget in Indian Rupees (₹), available cooking time, and any dietary restrictions.
2. Call get_meal_suggestions with those values to find candidates.
3. For each candidate returned, evaluate it using Strands Decider 2B (the MealSuitabilityGuard, already wired in). You will receive a list of pre-evaluated candidates with verdicts: 'allow', 'review', or 'block'.
4. Recommend the 'allow' meals first, then 'review' meals with a note about what might be missing. Skip 'block' meals entirely.
5. Always show prices in Indian Rupees (₹). For the top recommendation, offer to show recipe steps, cost breakdown, or nutrition info.

Be concise, practical, and warm. Never invent meals not in the catalogue."""


class HackathonAgent:
    """One Strands agent per session, with MealSuitabilityGuard running before the LLM."""

    def __init__(
        self,
        decider: Decider | None = None,
        model_id: str | None = None,
        eager: bool | None = None,
    ):
        import os

        self.decider = decider or Decider()
        self.eager = eager if eager is not None else os.environ.get("DEMO_EAGER") == "1"
        self.model_id = model_id or default_model_id()
        self.sessions: dict[str, tuple[Agent, MealSuitabilityGuard]] = {}

    def _session(self, session_id: str) -> tuple[Agent, MealSuitabilityGuard]:
        if session_id not in self.sessions:
            guard = MealSuitabilityGuard(self.decider)
            agent = Agent(
                model=agent_model(self.model_id),
                system_prompt=SYSTEM_PROMPT,
                tools=TOOLS,
                callback_handler=None,
            )
            self.sessions[session_id] = (agent, guard)
        return self.sessions[session_id]

    def _build_constraints_text(self, message: str) -> str:
        """Extract a plain-text constraints summary to pass to the Decider."""
        return f"User request: {message}"

    def _evaluate_candidates(
        self, guard: MealSuitabilityGuard, user_constraints: str, candidates: list[dict]
    ) -> list[dict]:
        """Run MealSuitabilityGuard on each candidate meal; attach verdict to each.

        Retries each decider call up to 3 times with backoff on 503/busy errors.
        Falls back to 'review' if the decider is still unreachable after retries.
        """
        import time as _time
        from decider_kit.client import DeciderError

        meals_by_id = {m["id"]: m for m in _meals()}
        evaluated = []
        for c in candidates:
            meal_id = c.get("id", "")
            full = meals_by_id.get(meal_id, c)
            meal_desc = (
                f"Ingredients: {', '.join(full.get('ingredients', []))}. "
                f"Prep time: {full.get('prep_time_min')} min. "
                f"Estimated cost: ₹{full.get('estimated_cost_inr')}. "
                f"Dietary tags: {', '.join(full.get('dietary_tags', [])) or 'none'}."
            )
            verdict = "review"  # safe fallback if decider is unavailable
            for attempt in range(3):
                try:
                    verdict = guard.check(user_constraints, c["name"], meal_desc)
                    break
                except DeciderError as e:
                    if "server busy" in str(e) or "503" in str(e) or "rate limit" in str(e):
                        wait = 4 * (attempt + 1)  # 4 s, 8 s, 12 s
                        _time.sleep(wait)
                    else:
                        break  # non-transient error, keep fallback
            evaluated.append({**c, "verdict": verdict})
        return evaluated

    def chat(
        self, message: str, session_id: str = "default", images: list[Any] | None = None
    ) -> dict[str, Any]:
        """Send a message to MealMind and get a reply with decision records."""
        agent, guard = self._session(session_id)
        before = len(guard.log)
        t0 = time.perf_counter()
        # Inject pre-evaluated candidate verdicts into the context when the message
        # looks like a meal-planning request (contains ingredient/budget keywords).
        keywords = ["have", "ingredient", "budget", "time", "minute", "vegetarian", "vegan",
                    "gluten", "halal", "cook", "make", "eat", "meal", "food", "diet", "rupee", "inr", "₹"]
        if any(k in message.lower() for k in keywords):
            # Quick candidate scan so the Decider runs before the LLM
            from .tools import _meals as all_meals
            from decider_kit.data import load as _load
            user_constraints = self._build_constraints_text(message)
            # Pull up to 6 candidates by simple ingredient overlap for pre-evaluation
            tokens = [w.strip(".,!?").lower() for w in message.split()]
            candidates = []
            for m in all_meals():
                meal_ings = [i.lower() for i in m.get("ingredients", [])]
                overlap = sum(1 for t in tokens if any(t in mi or mi in t for mi in meal_ings))
                if overlap > 0:
                    candidates.append({**m, "_overlap": overlap})
            candidates.sort(key=lambda c: -c["_overlap"])
            candidates = candidates[:3]  # limit to 3 to stay within hosted API rate limits
            if candidates:
                try:
                    evaluated = self._evaluate_candidates(guard, user_constraints, candidates)
                    verdicts_summary = "\n".join(
                        f"- {e['name']}: {e['verdict'].upper()} (cost ₹{e.get('estimated_cost_inr')}, "
                        f"{e.get('prep_time_min')} min, tags: {', '.join(e.get('dietary_tags', [])) or 'none'})"
                        for e in evaluated
                    )
                    augmented = (
                        f"{message}\n\n"
                        f"[MealMind pre-evaluation by Strands Decider 2B — use these verdicts to guide your recommendation]\n"
                        f"{verdicts_summary}\n"
                        f"ALLOW = great fit, REVIEW = partial fit (mention caveat), BLOCK = skip entirely."
                    )
                    result = agent(augmented)
                except Exception:
                    # Decider unavailable — run without pre-evaluation, LLM uses tool results directly
                    result = agent(message)
            else:
                result = agent(message)
        else:
            result = agent(message)

        reply = strip_thinking(str(result))
        return {
            "reply": reply,
            "decisions": guard.log[before:],
            "model_id": self.model_id,
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "agent": NAME,
            "eager": self.eager,
        }


if __name__ == "__main__":
    import json
    import sys

    a = HackathonAgent()
    for msg in sys.argv[1:] or [
        "I have rice, eggs, onion, and soy sauce. Budget ₹400, 25 min, I'm vegetarian.",
        "What are the steps for the first one?",
    ]:
        print(json.dumps(a.chat(msg), indent=1))
