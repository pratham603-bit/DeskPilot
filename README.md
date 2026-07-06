# DeskPilot — A Personal Productivity Agent

DeskPilot is a personal productivity agent that manages tasks, schedules, and documents through natural language. Powered by Gemini function calling with persistent memory of user preferences, it collapses disconnected tools (to-do lists, calendars, and notes) into a single conversational interface.

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

## Features
- **Task Management**: Add, list, and complete tasks with priority and due dates.
- **Calendar & Scheduling**: Schedule events, check for overlapping conflicts, and get daily briefings.
- **Persistent Memory**: Remembers your preferences across sessions (e.g., "always summarize concisely").
- **Web Interface & CLI**: Comes with both a beautiful browser-based chat UI and a fast terminal CLI.
- **Audit Logging**: Every action taken by the LLM is logged for complete traceability.

## Setup Instructions
1. Clone the repository.
2. Initialize a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
4. Run the Web UI:
   ```bash
   .\run_web.bat
   ```
   Or run the Terminal CLI:
   ```bash
   .\run.bat
   ```

## Course Concepts Applied (5-Day AI Agents Intensive)
- **Tool Integration:** Tools are fully integrated into `tools.py` with rigorous validation and error handling as per best practices.
- **Agent Skills & Memory:** Implemented in `memory.py` and documented in `.agent/skills/productivity-assistant/SKILL.md`. DeskPilot remembers preferences across sessions.
- **Security & STRIDE:** We implemented a `THREAT_MODEL.md` that addresses prompt injection, DOS, and Information Disclosure risks. All tool executions are securely logged in `data/audit.log`.
- **Testing:** Comprehensive `pytest` suite ensuring correct task management and conflict resolution.

## Limitations & Future Work
- **Local-only for now.** `api.py` serves the Flask UI locally; next steps include deploying to Cloud Run.
- **No external calendar integration.** Events are stored in SQLite; future work could sync with Google Calendar via the Calendar API.
