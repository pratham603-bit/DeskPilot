import sqlite3
import os
import json
import datetime
from typing import Optional, List, Dict, Any
import functools
import google.generativeai as genai
from memory import remember_preference as mem_remember_preference, get_preferences

DB_FILE = os.path.join(os.path.dirname(__file__), "data", "tasks.db")
AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), "data", "audit.log")

def _init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            )
        ''')
        conn.commit()

_init_db()

def _audit_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().isoformat()
        tool_name = func.__name__
        arguments = {"args": args, "kwargs": kwargs}
        try:
            result = func(*args, **kwargs)
            log_entry = {
                "timestamp": timestamp,
                "tool": tool_name,
                "arguments": arguments,
                "result": result
            }
        except Exception as e:
            result = f"Error: {str(e)}"
            log_entry = {
                "timestamp": timestamp,
                "tool": tool_name,
                "arguments": arguments,
                "error": result
            }
        
        os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return result
    return wrapper

@_audit_log
def add_task(title: str, due_date: str = "", priority: str = "medium") -> str:
    """Adds a new task to the database."""
    if not title or not title.strip():
        return "Error: Task title cannot be empty."
    if priority not in ["low", "medium", "high"]:
        return "Error: Priority must be 'low', 'medium', or 'high'."
    
    if due_date:
        try:
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return "Error: due_date must be in YYYY-MM-DD format."
            
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (title, due_date, priority, status) VALUES (?, ?, ?, ?)",
                (title.strip(), due_date if due_date else None, priority, "pending")
            )
            conn.commit()
            return f"Successfully added task: '{title}' with ID {cursor.lastrowid}."
    except Exception as e:
        return f"Database error: {str(e)}"

@_audit_log
def list_tasks(filter_status: str = "all") -> str:
    """Lists tasks from the database."""
    if filter_status not in ["all", "pending", "completed"]:
        return "Error: filter_status must be 'all', 'pending', or 'completed'."
        
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            if filter_status == "all":
                cursor.execute("SELECT id, title, due_date, priority, status FROM tasks")
            else:
                cursor.execute("SELECT id, title, due_date, priority, status FROM tasks WHERE status = ?", (filter_status,))
            rows = cursor.fetchall()
            
            if not rows:
                return "No tasks found."
                
            res = []
            for row in rows:
                res.append(f"[{row[0]}] {row[1]} (Priority: {row[3]}, Due: {row[2]}, Status: {row[4]})")
            return "\n".join(res)
    except Exception as e:
        return f"Database error: {str(e)}"

@_audit_log
def complete_task(task_id: int) -> str:
    """Marks a task as completed."""
    if not isinstance(task_id, int) or task_id <= 0:
        return "Error: task_id must be a positive integer."
        
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return f"Error: Task ID {task_id} not found."
            if row[0] == "completed":
                return f"Error: Task ID {task_id} is already completed."
                
            cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
            conn.commit()
            return f"Successfully marked task {task_id} as completed."
    except Exception as e:
        return f"Database error: {str(e)}"

@_audit_log
def schedule_event(title: str, start_time: str, end_time: str) -> str:
    """Schedules a new event."""
    if not title or not title.strip():
        return "Error: Event title cannot be empty."
        
    try:
        start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Error: Times must be in 'YYYY-MM-DD HH:MM' format."
        
    if end_dt <= start_dt:
        return "Error: end_time must be after start_time."
        
    conflicts = _get_conflicts(start_time, end_time)
    if conflicts:
        return f"Error: Cannot schedule event due to conflicts:\n{conflicts}"
        
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (title, start_time, end_time) VALUES (?, ?, ?)",
                (title.strip(), start_time, end_time)
            )
            conn.commit()
            return f"Successfully scheduled event: '{title}' from {start_time} to {end_time}."
    except Exception as e:
        return f"Database error: {str(e)}"

def _get_conflicts(start_time: str, end_time: str) -> str:
    """Internal helper to find overlapping events."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, start_time, end_time FROM events WHERE start_time < ? AND end_time > ?",
                (end_time, start_time)
            )
            rows = cursor.fetchall()
            if not rows:
                return ""
            res = []
            for row in rows:
                res.append(f"[{row[0]}] {row[1]} ({row[2]} to {row[3]})")
            return "\n".join(res)
    except Exception:
        return ""

@_audit_log
def check_conflicts(start_time: str, end_time: str) -> str:
    """Checks for overlapping events."""
    try:
        start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Error: Times must be in 'YYYY-MM-DD HH:MM' format."
        
    if end_dt <= start_dt:
        return "Error: end_time must be after start_time."
        
    conflicts = _get_conflicts(start_time, end_time)
    if not conflicts:
        return "No scheduling conflicts found."
    return f"Conflicts found:\n{conflicts}"

@_audit_log
def summarize_document(text: str) -> str:
    """Summarizes document text using Gemini API."""
    if not text or not text.strip():
        return "Error: Document text cannot be empty."
        
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"Summarize the following document and extract action items:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

@_audit_log
def daily_briefing() -> str:
    """Returns today's tasks, events, and user preferences."""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    tasks_res = []
    events_res = []
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, priority, status FROM tasks WHERE due_date = ? OR status = 'pending'", (today_str,))
            task_rows = cursor.fetchall()
            for row in task_rows:
                tasks_res.append(f"- [{row[0]}] {row[1]} (Priority: {row[2]}, Status: {row[3]})")
                
            cursor.execute("SELECT id, title, start_time, end_time FROM events WHERE start_time LIKE ?", (today_str + "%",))
            event_rows = cursor.fetchall()
            for row in event_rows:
                events_res.append(f"- [{row[0]}] {row[1]} ({row[2]} to {row[3]})")
    except Exception as e:
        return f"Database error: {str(e)}"
        
    prefs = get_preferences()
    
    briefing = "## Daily Briefing ##\n\n"
    briefing += "**Preferences:**\n" + prefs + "\n\n"
    
    briefing += "**Tasks:**\n"
    if tasks_res:
        briefing += "\n".join(tasks_res)
    else:
        briefing += "No tasks pending for today."
        
    briefing += "\n\n**Events Today:**\n"
    if events_res:
        briefing += "\n".join(events_res)
    else:
        briefing += "No events scheduled today."
        
    return briefing

@_audit_log
def remember_preference(key: str, value: str) -> str:
    """Saves a user preference."""
    if not key or not key.strip() or not value or not value.strip():
        return "Error: Preference key and value cannot be empty."
    return mem_remember_preference(key.strip(), value.strip())
