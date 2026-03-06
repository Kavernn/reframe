from db import get_json, set_json
from datetime import datetime

def load_sessions() -> dict:
    return get_json("sessions", {})

def save_sessions(sessions: dict):
    set_json("sessions", sessions)

def log_session(date: str, rpe, comment: str, exos: list):
    sessions = load_sessions()
    sessions[date] = {
        "rpe":       rpe,
        "comment":   comment,
        "exos":      exos,
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_sessions(sessions)

def get_last_sessions(n: int = 10) -> list:
    sessions = load_sessions()
    result   = []
    for date in sorted(sessions.keys(), reverse=True)[:n]:
        entry = sessions[date].copy()
        entry["date"] = date
        result.append(entry)
    return result

def migrate_sessions_from_weights(weights: dict) -> int:
    return 0