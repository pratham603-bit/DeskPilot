import json
import os
from typing import Dict, Any

PREFS_FILE = os.path.join(os.path.dirname(__file__), "data", "preferences.json")

def load_preferences() -> Dict[str, Any]:
    """Loads user preferences from the JSON file."""
    if not os.path.exists(PREFS_FILE):
        return {}
    
    with open(PREFS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_preferences(prefs: Dict[str, Any]) -> None:
    """Saves user preferences to the JSON file."""
    os.makedirs(os.path.dirname(PREFS_FILE), exist_ok=True)
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4)

def remember_preference(key: str, value: str) -> str:
    """Stores a new preference key-value pair and returns a success message."""
    prefs = load_preferences()
    prefs[key] = value
    save_preferences(prefs)
    return f"Successfully remembered preference: {key} = {value}"

def get_preferences() -> str:
    """Returns all current preferences as a string."""
    prefs = load_preferences()
    if not prefs:
        return "No preferences found."
    
    return "Current Preferences:\n" + "\n".join([f"- {k}: {v}" for k, v in prefs.items()])
