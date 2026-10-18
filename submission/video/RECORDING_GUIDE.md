# MealMind Demo Video — Recording Guide

## Quick facts
- App URL: http://localhost:8501
- Start command: `.venv\Scripts\python.exe -m uvicorn demo.server:app --host 0.0.0.0 --port 8501`
- UI: dark-themed chat panel (left) + Strands Decider 2B live decision panel (right)
- Target length: 2 min 30 sec
- Export: 1920x1080 MP4, H.264, 30 fps

---

## Scene-by-scene script

### SCENE 1 — Title card (0:00 – 0:12)
**On screen:** Black background. Text fades in:
  - Line 1 (large): "MealMind"
  - Line 2 (medium): "An AI Meal Planner That Decides Before It Recommends"
  - Line 3 (small, orange): "Built with Strands Decider 2B · Amazon Bedrock · Strands Agents"

**Narration (read aloud or record voice-over):**
> "Every day, millions of people stare into their fridge and ask the same question:
> what can I actually make with what I have?
> MealMind answers that question — and it uses AI to make sure the answer is right."

---

### SCENE 2 — Problem statement (0:12 – 0:28)
**On screen:** Simple slide or text overlay on dark background:
  - "The Problem"
  - Bullet 1: "Generic recipe apps ignore your actual ingredients"
  - Bullet 2: "LLMs hallucinate meals you can't afford or make"
  - Bullet 3: "No awareness of dietary restrictions or cooking time"

**Narration:**
> "Most meal planners either show you everything and leave the filtering to you,
> or they recommend meals that don't match what you actually have at home.
> MealMind is different. Before it recommends anything, it checks."

---

### SCENE 3 — Introduce MealMind (0:28 – 0:45)
**On screen:** Switch to browser showing http://localhost:8501 — the full UI visible.
  Show the header: agent name "MealMind — AI Meal Planner", LLM info, Decider info.
  Right panel reads: "Decisions appear here as the agent makes them."

**Narration:**
> "MealMind is an AI meal planner built with Strands Agents and Amazon Bedrock.
> The left panel is the conversation. The right panel shows every decision
> Strands Decider 2B makes — in real time, before the agent says a word."

**On-screen text overlay (lower third):** "http://localhost:8501 · FastAPI + Uvicorn backend"

---

### SCENE 4 — Live demo: Turn 1 (0:45 – 1:15)
**Action:** Click into the message box and type slowly so it is readable:
  `I have rice, eggs, onion, soy sauce, and carrot. My budget is ₹400, I have 25 minutes, and I'm vegetarian.`
  Press Send. Wait for the response (10–30 seconds on the hosted LLM).

**While waiting — narration:**
> "I tell MealMind what I have: rice, eggs, onion, soy sauce, carrot.
> Budget: 400 rupees. Time: 25 minutes. And I'm vegetarian.
> Before the LLM writes a single word, Strands Decider 2B runs a policy check
> on every candidate meal."

**When the response arrives — zoom into the RIGHT panel (decision panel):**
  Show the decision cards appearing. Each card shows:
  - meal name
  - verdict tag: ALLOW (green), REVIEW (amber), or BLOCK (red)
  - probability bars for meal_fits_ingredients, meal_fits_constraints, dietary_safe

**Narration (over the decision panel):**
> "Each decision card shows three questions the Decider answered:
> Can it be made from these ingredients? Does it fit the budget and time?
> Is it safe for a vegetarian?
> A green ALLOW means all three checks passed.
> An amber REVIEW means one constraint was marginal.
> A red BLOCK means the meal was skipped entirely — never shown to the user."

---

### SCENE 5 — Architecture explanation (1:15 – 1:40)
**On screen:** Switch to a slide or annotated diagram. You can use the architecture image:
  - User types message
  - -> MealSuitabilityGuard (Strands Decider 2B): 3 questions, 1 forward pass per meal
  - -> Strands Agent (Amazon Bedrock Nova Pro): receives verdicts, generates reply
  - -> Tools: get_meal_suggestions, get_recipe_steps, estimate_cost, get_nutritional_info
  - -> Amazon Bedrock AgentCore Runtime (deployment)

**Narration:**
> "Here is how MealMind works under the hood.
> When you send a message, MealSuitabilityGuard runs first.
> It calls Strands Decider 2B once per candidate meal — answering three typed questions
> in a single forward pass of a 2-billion-parameter decision model.
> The verdicts are injected into the Strands Agent's context.
> Amazon Bedrock Nova Pro then writes the reply, already knowing what to recommend
> and what to skip. The result: faster, cheaper, and more reliable recommendations."

**On-screen text overlay:** "One forward pass = 3 answers · ~1.2s per meal · No extra LLM calls"

---

### SCENE 6 — Live demo: Turn 2 — recipe steps (1:40 – 1:55)
**Action:** Type: `What are the steps for making the first one?`
  Press Send. Wait for response.

**Narration:**
> "Once MealMind recommends a meal, I can ask for the recipe.
> No Decider call needed here — this is a straightforward tool lookup."

**On screen:** Show the recipe steps appearing in the left chat panel.
  Note the right panel: no new decision cards (because no classification was needed).

---

### SCENE 7 — Live demo: Turn 3 — dietary block in action (1:55 – 2:15)
**Action:** Type: `I only have bread and cheese. Budget ₹250, 10 minutes. I'm vegetarian.`
  Press Send. Wait for response.

**Narration:**
> "Now a simpler request — bread and cheese, 250 rupees, 10 minutes.
> Watch the decision panel on the right.
> The Decider evaluates each candidate. Meals with meat are blocked immediately —
> they never appear in the recommendation, even as a suggestion."

**On screen:** Highlight a BLOCK card (red) in the right panel if one appears.
  Zoom in on the dietary_safe probability bar showing a low value (red bar).

---

### SCENE 8 — Live demo: Turn 4 — nutrition info (2:15 – 2:25)
**Action:** Type: `Is the grilled cheese sandwich gluten-free? And how many calories?`
  Press Send. Wait.

**Narration:**
> "Finally — nutritional info and dietary details on demand.
> Grilled cheese: vegetarian, 370 calories, 60 rupees."

---

### SCENE 9 — Closing (2:25 – 2:35)
**On screen:** Return to dark slide:
  - "MealMind"
  - "Strands Decider 2B · Amazon Bedrock · Strands Agents · AgentCore Runtime"
  - "One decision model. Calibrated confidence. No wasted LLM calls."
  - Footer: "Built with the AWS User Group Madurai Strands Decider hackathon kit"
  - "github.com/srikumaran130310-ship-it/mealmind"

**Narration:**
> "MealMind shows how a small, fast decision model can make an AI agent
> more reliable and cheaper — without replacing the LLM.
> Strands Decider 2B runs one forward pass per meal. The agent gets calibrated answers.
> The user gets recommendations they can actually cook.
> Built with the AWS User Group Madurai Strands Decider hackathon kit."

---

## Recording checklist

Before you start:
- [ ] Browser zoom set to 100%
- [ ] Window maximised to full screen (1920x1080)
- [ ] http://localhost:8501 loaded and showing "MealMind — AI Meal Planner" in the header
- [ ] Right panel shows "Decisions appear here as the agent makes them."
- [ ] Screen recorder started (OBS, Loom, or Windows Game Bar Win+G)
- [ ] Microphone test done — no background noise
- [ ] Phone/notifications silenced

Scene by scene:
- [ ] Scene 1: Title card (create in PowerPoint, Canva, or OBS overlay — 12 sec)
- [ ] Scene 2: Problem slide (12 sec) — can reuse title slide with new text
- [ ] Scene 3: Browser open, header visible, both panels visible (17 sec)
- [ ] Scene 4: Type Turn 1, wait for response, zoom decision panel (30 sec)
- [ ] Scene 5: Architecture slide (25 sec)
- [ ] Scene 6: Type Turn 2, show recipe steps (15 sec)
- [ ] Scene 7: Type Turn 3, highlight BLOCK card (20 sec)
- [ ] Scene 8: Type Turn 4, show nutrition (10 sec)
- [ ] Scene 9: Closing slide (10 sec)

After recording:
- [ ] Trim silences between turns
- [ ] Add lower-third text overlays (scene labels, URL, tech stack)
- [ ] Add narration track (record separately and sync, or use text-to-speech)
- [ ] Export 1920x1080 MP4 H.264, 30 fps, AAC audio 192kbps

---

## Recommended free tools

| Task | Windows tool |
|---|---|
| Screen recording | OBS Studio (free, obsproject.com) or Win+G (Xbox Game Bar, built-in) |
| Video editing | DaVinci Resolve (free, blackmagicdesign.com) or Clipchamp (built into Windows 11) |
| Slides for title/arch | Canva (free, canva.com) or PowerPoint |
| Voice-over | Windows Voice Recorder, then import into editor |

---

## OBS quick setup for 1080p

1. Open OBS. Add Source -> Display Capture (or Window Capture -> Chrome/Edge).
2. Settings -> Video -> Base Resolution: 1920x1080, Output: 1920x1080, FPS: 30.
3. Settings -> Output -> Recording Format: mp4, Encoder: H.264.
4. Start Recording before Scene 3. Stop after Scene 9.
5. Record slides separately as screen captures, then splice in the editor.

---

## Architecture slide content (copy into Canva/PowerPoint)

Title: "How MealMind Works"

Flow (left to right):
User Input
  -> [MealSuitabilityGuard]
       Strands Decider 2B
       3 questions · 1 forward pass · ~1.2s
       meal_fits_ingredients (noul)
       meal_fits_constraints (choice)
       dietary_safe (noul)
       Verdict: ALLOW / REVIEW / BLOCK
  -> [Strands Agent]
       Amazon Bedrock Nova Pro
       Receives verdicts in context
       Calls tools as needed
  -> [Tools]
       get_meal_suggestions
       get_recipe_steps
       estimate_cost
       get_nutritional_info
  -> Reply to user

Deployment: Amazon Bedrock AgentCore Runtime
