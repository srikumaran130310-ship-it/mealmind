"""
MealMind demo helper — pre-fills each turn via the API so you can focus on the screen.

Usage (run AFTER the server is up at http://localhost:8501):
    .venv\Scripts\python.exe submission\video\demo_helper.py

What it does:
  - Sends each demo turn to the /api/chat endpoint in sequence.
  - Prints the reply and each decision record to the terminal.
  - Pauses between turns so you can switch to the browser and record the result.
  - Does NOT change any project files or tests.

Recording tip: have this script running in a terminal alongside the browser.
After each "Press Enter to continue" prompt, switch to the browser window — the
response is already there, ready to record.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8501"
SESSION = "video-demo"

TURNS = [
    {
        "label": "TURN 1 — Main meal planning request",
        "message": "I have rice, eggs, onion, soy sauce, and carrot. My budget is \u20b9400, I have 25 minutes, and I'm vegetarian.",
        "narration": "Watch the right panel — Strands Decider 2B evaluates each candidate meal.",
    },
    {
        "label": "TURN 2 — Recipe steps",
        "message": "What are the steps for making the first one?",
        "narration": "Straightforward tool lookup — no Decider call needed here.",
    },
    {
        "label": "TURN 3 — Dietary block demo",
        "message": "I only have bread and cheese. Budget \u20b9250, 10 minutes. I'm vegetarian.",
        "narration": "Watch for BLOCK verdicts on non-vegetarian candidates in the decision panel.",
    },
    {
        "label": "TURN 4 — Nutrition info",
        "message": "Is the grilled cheese sandwich gluten-free? And how many calories does it have?",
        "narration": "Nutrition and dietary info from the catalogue.",
    },
]


def send(message: str, session_id: str) -> dict:
    body = json.dumps({"message": message, "session_id": session_id}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()[:300]}
    except Exception as e:
        return {"error": str(e)}


def check_server() -> bool:
    try:
        with urllib.request.urlopen(f"{BASE}/api/info", timeout=5) as r:
            info = json.loads(r.read())
            print(f"  Agent : {info.get('agent')}")
            print(f"  LLM   : {info.get('llm')}")
            print(f"  Decider: {info.get('decider')}")
            return True
    except Exception as e:
        print(f"  ERROR: cannot reach {BASE} — {e}")
        return False


def print_decision(d: dict) -> None:
    verdict = d.get("verdict") or d.get("action") or "?"
    meal = d.get("meal") or d.get("tool") or d.get("stage") or ""
    probs = {k: v for k, v in d.items() if isinstance(v, float) and 0 <= v <= 1 and not k.endswith("_ms")}
    bar = lambda p: ("█" * int(p * 10)).ljust(10) + f" {p:.2f}"
    print(f"    [{verdict.upper():8}] {meal}")
    for k, v in probs.items():
        print(f"              {k:<35} {bar(v)}")
    print(f"              decider_ms: {d.get('decider_ms', '?')}")


def main() -> None:
    print("\n" + "=" * 60)
    print("  MealMind Demo Helper")
    print("=" * 60)
    print(f"\nChecking server at {BASE} ...")
    if not check_server():
        print("\nStart the server first:")
        print("  .venv\\Scripts\\python.exe -m uvicorn demo.server:app --host 0.0.0.0 --port 8501")
        sys.exit(1)

    print("\nServer is up. Open http://localhost:8501 in your browser and start your screen recorder.\n")
    input("Press Enter when ready to begin Turn 1 ...")

    for i, turn in enumerate(TURNS, 1):
        print(f"\n{'─'*60}")
        print(f"  {turn['label']}")
        print(f"  Narration cue: {turn['narration']}")
        print(f"  Message: {turn['message']}")
        print(f"{'─'*60}")
        print("  Sending to agent (this may take 15-30 seconds)...")

        out = send(turn["message"], SESSION)

        if "error" in out:
            print(f"\n  ERROR: {out['error']}")
            print("  (Check if the decider API is available. The agent will fall back gracefully.)")
        else:
            print(f"\n  REPLY ({out.get('latency_ms')} ms):")
            print(f"  {out.get('reply', '')[:400]}")
            decisions = out.get("decisions", [])
            if decisions:
                print(f"\n  DECISIONS ({len(decisions)} Decider calls):")
                for d in decisions:
                    print_decision(d)
            else:
                print("  (No Decider calls this turn — tool lookup only.)")

        print("\n  >>> Switch to the browser now and record the result. <<<")
        if i < len(TURNS):
            input(f"\n  Press Enter when ready for Turn {i + 1} ...")

    print("\n" + "=" * 60)
    print("  All turns complete! Stop your screen recorder.")
    print("  Now edit your footage using the guide in:")
    print("  submission/video/RECORDING_GUIDE.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
