from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not _SUPABASE_URL or not _SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables.")

_client: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
_TABLE = "kv"


def _single_or_none(resp) -> Optional[dict]:
    data = getattr(resp, "data", None)
    if isinstance(data, list):
        return data[0] if data else None
    return data


def get_json(key: str, default: Any = None) -> Any:
    """Return JSON value for key or default if missing/error."""
    try:
        resp = _client.table(_TABLE).select("value").eq("key", key).single().execute()
        row = _single_or_none(resp)
        if row is None:
            return default
        return row.get("value", default)
    except Exception as e:
        print(f"[DB] get_json({key}) error: {e}")
        return default


def set_json(key: str, value: Any) -> bool:
    """Upsert JSON value for key."""
    try:
        _client.table(_TABLE).upsert({"key": key, "value": value}).execute()
        return True
    except Exception as e:
        print(f"[DB] set_json({key}) error: {e}")
        return False


def update_json(key: str, patch: Dict[str, Any]) -> Any:
    """Merge dict patch into existing JSON (dict) and save."""
    base = get_json(key, {}) or {}
    if not isinstance(base, dict):
        base = {}
    base.update(patch)
    ok = set_json(key, base)
    return base if ok else None


def append_json_list(key: str, entry: Any, max_items: Optional[int] = None) -> list:
    """Insert entry at head of list under key; truncate to max_items if provided."""
    arr = get_json(key, []) or []
    if not isinstance(arr, list):
        arr = []
    arr.insert(0, entry)
    if max_items:
        arr = arr[:max_items]
    set_json(key, arr)
    return arr


def client() -> Client:
    return _client