# api/inventory.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
from .db import get_json, set_json

# Inventaire par défaut (repris de ta version fichier)
DEFAULT_INVENTORY: Dict[str, Any] = {
    "Bench Press": {
        "type": "barbell",
        "increment": 5.0,
        "bar_weight": 45.0,
        "default_scheme": "4x5-7",
        "muscles": ["pectoraux", "triceps", "deltoïdes antérieurs"],
    },
    "Incline DB Press": {
        "type": "dumbbell",
        "increment": 5.0,
        "default_scheme": "3x8-12",
        "muscles": ["pectoraux supérieurs", "deltoïdes antérieurs", "triceps"],
    },
    "Back Squat": {
        "type": "barbell",
        "increment": 5.0,
        "bar_weight": 45.0,
        "default_scheme": "4x5-8",
        "muscles": ["quadriceps", "fessiers", "ischio-jambiers", "bas du dos", "abdos"],
    },
    "Leg Press": {
        "type": "machine",
        "increment": 10.0,
        "default_scheme": "3x10-15",
        "muscles": ["quadriceps", "fessiers", "ischio-jambiers"],
    },
    "Lat Pulldown": {
        "type": "machine",
        "increment": 5.0,
        "default_scheme": "3x8-12",
        "muscles": ["grand dorsal", "biceps", "rhomboïdes", "trapèzes"],
    },
}

KEY = "inventory"

def load_inventory() -> Dict[str, Any]:
    """
    Charge l'inventaire depuis Supabase KV.
    Retourne DEFAULT_INVENTORY si clé absente/vide.
    """
    data = get_json(KEY, {}) or {}
    if not isinstance(data, dict) or not data:
        return DEFAULT_INVENTORY.copy()
    return data

def save_inventory(inventory: Dict[str, Any]) -> None:
    set_json(KEY, inventory)

def add_exercise(
    name: str,
    ex_type: str,
    increment: float,
    bar_weight: float = 45.0,
    default_scheme: str = "3x8-12",
    muscles: Optional[List[str]] = None,
) -> None:
    """Ajoute ou met à jour un exercice dans l'inventaire (KV)."""
    inv = load_inventory()
    inv[name] = {
        "type": ex_type,
        "increment": float(increment),
        "bar_weight": float(bar_weight) if ex_type == "barbell" else 0.0,
        "default_scheme": default_scheme,
        "muscles": muscles or [],
    }
    save_inventory(inv)
    print(f"✅ '{name}' ajouté/mis à jour")

def calculate_plates(target_weight: float, bar_weight: float = 45.0) -> List[float]:
    """
    Liste des disques par côté pour atteindre `target_weight` total.
    Retourne une liste de plaques (45, 35, 25, 10, 5, 2.5).
    """
    if not target_weight or target_weight <= bar_weight:
        return []
    weight_per_side = (target_weight - bar_weight) / 2
    plates = [45, 35, 25, 10, 5, 2.5]
    needed: List[float] = []
    temp = round(float(weight_per_side), 2)
    for p in plates:
        while temp >= p:
            needed.append(p)
            temp = round(temp - p, 2)
    return needed