# api/sessions.py
from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime

from .db import get_json, set_json

KEY = "sessions"

def load_sessions() -> Dict[str, Any]:
    """
    Charge les sessions depuis Supabase KV.
    Retourne {} si la clé est absente ou invalide.
    """
    data = get_json(KEY, {}) or {}
    return data if isinstance(data, dict) else {}

def save_sessions(sessions: Dict[str, Any]) -> None:
    set_json(KEY, sessions)

def log_session(date: str, rpe: Optional[int], comment: str, exos: List[str]) -> None:
    sessions = load_sessions()
    sessions[date] = {
        "rpe": rpe,
        "comment": comment,
        "exos": exos,
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    save_sessions(sessions)

def get_last_sessions(n: int = 10) -> List[Dict[str, Any]]:
    sessions = load_sessions()
    result: List[Dict[str, Any]] = []
    for date_key in sorted(sessions.keys(), reverse=True)[:n]:
        entry = sessions[date_key].copy()
        entry["date"] = date_key
        result.append(entry)
    return result

def migrate_sessions_from_weights(weights: Dict[str, Any]) -> int:
    """
    Migre les sessions présentes dans weights["sessions"] → KV["sessions"] (one-shot).
    Retourne le nombre de sessions migrées.
    """
    old_sessions = (weights or {}).get("sessions", {})
    if not old_sessions:
        return 0

    sessions = load_sessions()
    count = 0
    for date_key, data in old_sessions.items():
        if date_key not in sessions:
            sessions[date_key] = {
                "rpe": data.get("rpe"),
                "comment": data.get("comment", ""),
                "exos": data.get("exos", []),
                "logged_at": data.get("logged_at", date_key),
            }
            count += 1
    save_sessions(sessions)
    return count