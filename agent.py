import os
import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from tools import (
    add_task, list_tasks, complete_task, schedule_event,
    check_conflicts, summarize_document, daily_briefing, remember_preference
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_INSTRUCTION = f"""
You are DeskPilot, a concise, proactive personal productivity agent.
You manage tasks, schedules, and documents through natural language.
Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}. Use this to resolve relative dates like "tomorrow" to YYYY-MM-DD.
RULES:
1. Be concise and direct in your responses.
2. Be proactive: if a user schedules an event, optionally tell them what tasks are due.
3. NEVER fabricate task or schedule data.
4. ALWAYS call a tool to check the database before answering questions about tasks or events.
5. ALWAYS respect user preferences.
"""

# Map of tool names to actual python functions
AVAILABLE_TOOLS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "schedule_event": schedule_event,
    "check_conflicts": check_conflicts,
    "summarize_document": summarize_document,
    "daily_briefing": daily_briefing,
    "remember_preference": remember_preference
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    tools=list(AVAILABLE_TOOLS.values())
)

def chat(message: str, history: list) -> str:
    """
    Main chat loop that processes user message, handles tool calls via SDK,
    and returns final text response.
    """
    try:
        # Convert history to standard genai format if not already
        formatted_history = []
        for msg in history:
            role = msg.get("role")
            parts = msg.get("parts", [])
            formatted_history.append({"role": role, "parts": parts})
            
        chat_session = model.start_chat(
            history=formatted_history,
            enable_automatic_function_calling=True
        )
        response = chat_session.send_message(message)
        return response.text
            
    except Exception as e:
        return f"DeskPilot encountered an error: {str(e)}"
