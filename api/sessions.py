# api/sessions.py
from __future__ import annotations

import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

# Chemin vers data/ à la racine
BASE_DIR = Path(__file__).parent            # /trainingOS/api
DATA_DIR = BASE_DIR.parent / "data"         # /trainingOS/data
SESSIONS_FILE = DATA_DIR / "sessions.json"

def load_sessions() -> Dict[str, Any]:
    if not SESSIONS_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return {}
    try:
        return json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] Lecture {SESSIONS_FILE} : {e}")
        return {}

def save_sessions(sessions: Dict[str, Any]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SESSIONS_FILE.write_text(
            json.dumps(sessions, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"Erreur sauvegarde sessions : {e}")

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
    Migre les sessions déjà présentes dans weights.json → sessions.json (one-shot).
    Retourne le nombre de sessions migrées.
    """
    old_sessions = weights.get("sessions", {})
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