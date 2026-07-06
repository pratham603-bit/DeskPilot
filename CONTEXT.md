# DeskPilot Project Context

This file contains the project purpose, scope boundaries, and coding standards for DeskPilot. Any AI agent (or human) working on this repository MUST adhere to these rules.

## Purpose
DeskPilot is a personal productivity agent that manages tasks, schedules, and documents through natural language, leveraging the Gemini API with function calling. It maintains a persistent local memory of user preferences and activities.

## Scope Boundaries
- **No Deletion**: DeskPilot must NEVER delete tasks, events, or preferences. It can only add or update (e.g., mark a task as completed).
- **No Fabrication**: The agent must never invent or hallucinate task or schedule data. It must strictly rely on what is returned by the database.
- **Local First**: All data (`tasks.db`, `preferences.json`, `audit.log`) must remain in the local `data/` directory.

## Coding Standards
- **Type Hints**: All functions must use standard Python type hints.
- **Docstrings**: Every function, class, and module must include a descriptive docstring.
- **Error Handling**: Functions in `tools.py` must never raise uncaught exceptions to the caller. All exceptions should be caught and returned as readable error string messages to be passed back to the LLM.
- **No Hardcoded Secrets**: Do not hardcode API keys or passwords. Always use `dotenv` and environment variables.
- **Testing**: All core logic in `tools.py` must be covered by `pytest` tests encompassing normal flows and edge cases.
