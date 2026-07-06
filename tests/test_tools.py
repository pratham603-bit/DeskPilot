import pytest
import sqlite3
import os
from unittest import mock
import tools
import memory

# Use a temporary SQLite database for testing to avoid connection isolation issues
TEST_DB = "test_tasks.db"

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Overrides DB path for tests and initializes tables."""
    monkeypatch.setattr(tools, "DB_FILE", TEST_DB)
    monkeypatch.setattr(tools, "AUDIT_LOG_FILE", "./test_audit.log")
    
    with sqlite3.connect(TEST_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tasks")
        cursor.execute("DROP TABLE IF EXISTS events")
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
    
    # Mock preferences file for testing
    monkeypatch.setattr(memory, "PREFS_FILE", "./test_prefs.json")
    
    yield
    
    # Cleanup any file artifacts created by the test
    if os.path.exists("./test_audit.log"):
        try:
            os.remove("./test_audit.log")
        except OSError:
            pass
    if os.path.exists("./test_prefs.json"):
        try:
            os.remove("./test_prefs.json")
        except OSError:
            pass

# Tests for add_task
def test_add_task_normal():
    res = tools.add_task("Buy groceries", "2024-12-31", "high")
    assert "Successfully added task" in res

def test_add_task_empty_title():
    res = tools.add_task("", "2024-12-31")
    assert "Error: Task title cannot be empty" in res

def test_add_task_invalid_date():
    res = tools.add_task("Buy groceries", "31-12-2024")
    assert "Error: due_date must be in YYYY-MM-DD format" in res

def test_add_task_invalid_priority():
    res = tools.add_task("Buy groceries", priority="super-high")
    assert "Error: Priority must be 'low', 'medium', or 'high'" in res

# Tests for complete_task
def test_complete_task_normal():
    tools.add_task("Test task")
    res = tools.complete_task(1)
    assert "Successfully marked task 1 as completed" in res

def test_complete_task_already_completed():
    tools.add_task("Test task 2")
    tools.complete_task(1)
    res = tools.complete_task(1)
    assert "is already completed" in res

def test_complete_task_nonexistent():
    res = tools.complete_task(999)
    assert "Error: Task ID 999 not found" in res

def test_complete_task_invalid_id():
    res = tools.complete_task(-5)
    assert "Error: task_id must be a positive integer" in res

# Tests for schedule_event & check_conflicts
def test_schedule_event_normal():
    res = tools.schedule_event("Meeting", "2024-01-01 10:00", "2024-01-01 11:00")
    assert "Successfully scheduled event" in res

def test_schedule_event_conflict():
    tools.schedule_event("Meeting 1", "2024-01-01 10:00", "2024-01-01 11:00")
    res = tools.schedule_event("Meeting 2", "2024-01-01 10:30", "2024-01-01 11:30")
    assert "Cannot schedule event due to conflicts" in res

def test_schedule_event_invalid_dates():
    res = tools.schedule_event("Meeting", "2024-01-01 11:00", "2024-01-01 10:00")
    assert "Error: end_time must be after start_time" in res

def test_schedule_event_empty_title():
    res = tools.schedule_event("", "2024-01-01 10:00", "2024-01-01 11:00")
    assert "Error: Event title cannot be empty" in res

# Tests for list_tasks
def test_list_tasks_normal():
    tools.add_task("Test task")
    res = tools.list_tasks()
    assert "Test task" in res

def test_list_tasks_empty():
    res = tools.list_tasks()
    assert "No tasks found" in res

def test_list_tasks_invalid_filter():
    res = tools.list_tasks("invalid")
    assert "Error: filter_status must be" in res

# Tests for memory/preferences
def test_remember_preference():
    res = tools.remember_preference("timezone", "PST")
    assert "Successfully remembered" in res
    assert "PST" in tools.daily_briefing()

def test_remember_preference_empty():
    res = tools.remember_preference("", "PST")
    assert "Error: Preference key and value cannot be empty" in res
