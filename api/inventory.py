# api/inventory.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
import json

# Dossiers
BASE_DIR = Path(__file__).parent                 # /trainingOS/api
DATA_DIR = BASE_DIR.parent / "data"              # /trainingOS/data
INVENTORY_FILE = DATA_DIR / "inventory.json"     # Fichier principal

# Inventaire par défaut (extraits représentatifs — tu peux enrichir au besoin)
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

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_inventory() -> Dict[str, Any]:
    """
    Charge inventory.json ; crée le fichier avec DEFAULT_INVENTORY s'il n'existe pas.
    Retourne toujours un dict.
    """
    _ensure_data_dir()
    if not INVENTORY_FILE.is_file():
        try:
            INVENTORY_FILE.write_text(
                json.dumps(DEFAULT_INVENTORY, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"[INFO] Fichier créé : {INVENTORY_FILE}")
            return DEFAULT_INVENTORY.copy()
        except Exception as e:
            print(f"[ERROR] Impossible de créer {INVENTORY_FILE} : {e}")
            return DEFAULT_INVENTORY.copy()

    try:
        data = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else DEFAULT_INVENTORY.copy()
    except Exception as e:
        print(f"[ERROR] Lecture {INVENTORY_FILE} : {e}")
        return DEFAULT_INVENTORY.copy()

def save_inventory(inventory: Dict[str, Any]) -> None:
    """Sauvegarde l'inventaire complet."""
    _ensure_data_dir()
    try:
        INVENTORY_FILE.write_text(
            json.dumps(inventory, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"Erreur sauvegarde inventaire : {e}")

def add_exercise(
    name: str,
    ex_type: str,
    increment: float,
    bar_weight: float = 45.0,
    default_scheme: str = "3x8-12",
    muscles: Optional[List[str]] = None,
) -> None:
    """Ajoute ou met à jour un exercice dans l'inventaire."""
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
    Calcule la liste des disques par côté pour atteindre `target_weight` total.
    Retourne une liste de plaques (45, 35, 25, 10, 5, 2.5).
    """
    if not target_weight or target_weight <= bar_weight:
        return []
    weight_per_side = (target_weight - bar_weight) / 2
    plates = [45, 35, 25, 10, 5, 2.5]
    needed: List[float] = []
    temp = round(float(weight_per_side), 2)  # éviter 2.499999
    for p in plates:
        while temp >= p:
            needed.append(p)
            temp = round(temp - p, 2)
    return needed