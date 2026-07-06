# 🚀 DeskPilot

**DeskPilot** is an AI-powered personal productivity agent that manages your tasks, schedule, and documents through natural language — powered by **Gemini 2.5 Flash** function calling, with persistent memory of your preferences.

> Chat with your productivity stack instead of clicking through it.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Task Management** | Add, list, and complete tasks with priorities and due dates |
| 📅 **Smart Scheduling** | Schedule events and automatically detect conflicts |
| 🧠 **Persistent Memory** | Remembers your preferences across sessions (e.g., "no meetings before 10am") |
| 📄 **Document Summaries** | Paste a document and get a Gemini-powered summary with action items |
| 🌅 **Daily Briefing** | Get a morning overview of pending tasks and today's events |
| 🌐 **Web UI + CLI** | Choose between a beautiful browser chat interface or a fast terminal CLI |
| 🔒 **Audit Logging** | Every tool call is logged to `data/audit.log` for full traceability |

---

## 🏗️ Architecture

```
User (Browser / Terminal)
        │
        ▼
    agent.py  ──── Gemini 2.5 Flash function-calling loop
        │
        ▼
    tools.py  ──── add_task · list_tasks · complete_task
                   schedule_event · check_conflicts
                   summarize_document · daily_briefing
                   remember_preference
        │                   │
        ▼                   ▼
  data/tasks.db        data/preferences.json
  (SQLite)             (via memory.py)
        │
        ▼
  data/audit.log  ──── append-only tool call ledger
        │
        ▼
  api.py  ──────────── Flask server → templates/index.html
```

---

## 🖥️ Screenshots

### Web Interface
> Start the web server and open `http://localhost:5000` in your browser.
> DeskPilot greets you with your daily briefing automatically.

### Terminal CLI
```
$ .\run.bat

Loading daily briefing...

You: Add a task: finish capstone report, due 2026-07-07, high priority
DeskPilot: Added "finish capstone report" (priority: high, due: 2026-07-07) to your task list.

You: What's on my schedule today?
DeskPilot: You have no events scheduled today.

You: Give me my daily briefing
DeskPilot: You have 1 open task — "finish capstone report" (high, due tomorrow) — and no events today.
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier works)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/DeskPilot.git
cd DeskPilot

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
copy .env.example .env
# Then edit .env and set: GEMINI_API_KEY=your_key_here
```

### Running

**Web Interface (recommended):**
```bash
.\run_web.bat
# Then open http://localhost:5000 in your browser
```

**Terminal CLI:**
```bash
.\run.bat
```

---

## 🧪 Tests

The project includes a full `pytest` suite with 17 tests covering normal and edge cases across every tool function (malformed dates, duplicate completions, overlapping event detection, etc.).

```bash
.\venv\Scripts\activate
pytest tests/ -v
```

---

## 📁 Project Structure

```
DeskPilot/
├── agent.py              # Gemini chat loop & system prompt
├── tools.py              # All tool functions (tasks, events, memory, docs)
├── memory.py             # Persistent preferences via JSON
├── api.py                # Flask API server
├── cli.py                # Terminal chat interface
├── templates/
│   └── index.html        # Web chat UI
├── data/
│   ├── .gitkeep
│   ├── tasks.db          # SQLite database (runtime, not committed)
│   ├── preferences.json  # User preferences (runtime, not committed)
│   └── audit.log         # Tool call log (runtime, not committed)
├── tests/
│   └── test_tools.py     # pytest suite
├── THREAT_MODEL.md       # STRIDE security analysis
├── run.bat               # Launch CLI (Windows)
└── run_web.bat           # Launch Web UI (Windows)
```

---

## 🔐 Security

A full STRIDE threat model is documented in [`THREAT_MODEL.md`](./THREAT_MODEL.md), covering:
- Prompt injection mitigations
- Input validation on every tool function
- Append-only audit logging for accountability
- `.env`-based secret management (never committed)

---

## 🗺️ Roadmap

- [ ] Deploy to Cloud Run for public access
- [ ] Google Calendar sync via the Calendar API
- [ ] Multi-user support with auth layer
- [ ] Recurring events support
- [ ] Voice input via the Web Speech API

---

## 📄 License

MIT — see [LICENSE](./LICENSE) for details.
