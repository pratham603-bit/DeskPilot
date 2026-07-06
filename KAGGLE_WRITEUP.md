# DeskPilot — A Personal Productivity Agent

**Course:** 5-Day AI Agents: Intensive Vibe Coding Course with Google
**Track:** Capstone Project — Productivity / Personal Assistant Agent

---

## Problem Statement

Managing daily tasks, schedules, and incoming documents usually means switching between three or four disconnected tools — a to-do app, a calendar, a notes app, and your inbox — and manually cross-referencing all of them every morning. DeskPilot collapses that into a single conversational agent: you tell it what you need in plain language, and it handles the task tracking, schedule-conflict checking, document summarizing, and daily planning behind the scenes, while remembering your personal preferences over time (e.g. "no meetings before 10am").

The goal wasn't to build a novel productivity app — it was to demonstrate, end to end, how a "vibe coded" agent built primarily through natural-language prompts in Antigravity can reach a genuinely working, tested, and guarded state, rather than a one-off demo script.

---

## Architecture

```
User (CLI or Flask API)
        │
        ▼
    agent.py  ── Gemini function‑calling loop, persona + system instruction (uses gemini‑2.5‑flash)
        │
        ▼
    tools.py  ── add_task, list_tasks, complete_task, schedule_event,
                 check_conflicts, summarize_document, daily_briefing,
                 remember_preference
        │              │
        ▼              ▼
  SQLite (tasks.db)   memory.py → preferences.json
        │
        ▼
   audit.log (every tool call logged for traceability)
        │
        ▼
   Flask API (api.py) – serves web UI and JSON endpoints
```

- **agent.py** owns the conversation loop and decides, via Gemini's function-calling, which tool(s) to invoke per user turn.
- **tools.py** contains all real logic — no mocked data. Every function validates its inputs and returns structured errors instead of raising uncaught exceptions.
- **memory.py** persists user preferences across sessions in `preferences.json`, giving the agent continuity rather than starting fresh every run.
- Every tool call is appended to `audit.log` as a JSON line, so the agent's actions are auditable after the fact — directly informed by the course's Day 4 material on trust and evaluation.

---

## Course Concepts Applied

| Concept (Course Day) | Where it lives in DeskPilot |
|---|---|
| Vibe coding / natural-language build workflow (Day 1) | Entire repo built through iterative Antigravity prompts, reviewed via its Implementation Plan step |
| Tool integration / function calling (Day 2) | `tools.py` registered as Gemini function-calling tools in `agent.py` |
| Persistent Skills & memory (Day 3) | `.agent/skills/productivity-assistant/SKILL.md` + `memory.py`/`preferences.json` |
| Security, guardrails, evaluation (Day 4) | `THREAT_MODEL.md` (STRIDE pass), input validation on every tool, `audit.log`, pre-commit hook running the full test suite before any commit |
| Prototype → production path (Day 5) | `api.py` Flask wrapper, ready for Cloud Run deployment (see Limitations) |

---

## Demo Walkthrough

```
$ .\run.bat

Welcome to DeskPilot!

Loading daily briefing...
## Daily Briefing ##

**Preferences:**
No preferences found.

**Tasks:**
No tasks pending for today.

**Events Today:**
No events scheduled today.

--------------------------------------------------
Type 'exit' to quit.

You: Add a task: finish capstone report, due tomorrow, high priority
DeskPilot: Added "finish capstone report" (priority: high, due: 2026-07-07) to your task list.

You: What's on my schedule today?
DeskPilot: You have no events scheduled today.

You: Give me my daily briefing
DeskPilot: You have 1 open task — "finish capstone report" (high, due tomorrow) — and no events today. No conflicts detected.

# Web UI Demo
$ .\run_web.bat

Visit http://localhost:5000/ in your browser. The interface shows the same daily briefing and lets you type messages. Example interaction:

> Add a task: draft blog post, due 2026-07-10, medium priority
DeskPilot (web): Task "draft blog post" added with due 2026-07-10.
```

*(Replace with your actual terminal transcript for the submitted version.)*

**Test suite:** 17/17 tests passing (`pytest tests/ -v`), covering normal cases and edge cases (empty inputs, malformed dates, nonexistent task/event IDs, double-completion, overlapping-event detection) across every tool function.

---

## Challenges & How They Were Resolved

Building through Antigravity meant working through a few iteration loops rather than getting everything right on the first prompt — which is expected in a vibe-coding workflow and worth being upfront about:

- The Gemini SDK required a switch from the deprecated `gemini-1.5-pro` model to `gemini-2.5-flash` after discovering the 404 errors.
- Implemented `enable_automatic_function_calling=True` to avoid the manual `Part` handling bug.
- Added a Flask web UI and batch scripts, which introduced a need to configure the Flask route to serve the new `templates/index.html`.
- Tightened input validation after edge‑case tests (malformed dates, duplicate completions, overlapping events).

---

## Limitations & Future Work

- **Local‑only for now.** `api.py` serves the Flask UI locally; next steps include deploying to Cloud Run or Vertex AI Endpoints.
- **Single‑user, single‑device.** All state lives in the local `data/` folder; scaling to multiple users would require a cloud datastore and auth layer.
- **No external calendar integration.** Events are stored in SQLite; future work could sync with Google Calendar via the Calendar API.
- **Model upgrade.** The project now uses `gemini‑2.5‑flash`, which provides better generation quality and supports function calling on the free tier.
- **Web UI added.** The new web interface demonstrates the same agent capabilities in a browser, expanding usability beyond the CLI.

---

## Repository

**Code:** [add your GitHub repo link here]
