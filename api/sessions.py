from db import get_json, set_json
from datetime import datetime

def load_sessions() -> dict:
    return get_json("sessions", {})

def save_sessions(sessions: dict):
    set_json("sessions", sessions)

def log_session(date: str, rpe, comment: str, exos: list, duration_min=None, energy_pre=None):
    sessions = load_sessions()
    entry = {
        "rpe":       rpe,
        "comment":   comment,
        "exos":      exos,
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    if duration_min is not None:
        entry["duration_min"] = duration_min
    if energy_pre is not None:
        entry["energy_pre"] = energy_pre
    sessions[date] = entry
    save_sessions(sessions)


def log_second_session(date: str, rpe, comment: str, exos: list, duration_min=None, energy_pre=None):
    """Ajoute une deuxième séance à la journée sans écraser la première."""
    sessions = load_sessions()
    entry = sessions.setdefault(date, {"exos": [], "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
    extra_entry = {
        "rpe":       rpe,
        "comment":   comment,
        "exos":      exos,
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    if duration_min is not None:
        extra_entry["duration_min"] = duration_min
    if energy_pre is not None:
        extra_entry["energy_pre"] = energy_pre
    entry.setdefault("extra_sessions", []).append(extra_entry)
    save_sessions(sessions)


def session_exists(date: str) -> bool:
    return date in load_sessions()

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