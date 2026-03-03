# inventory.py
from pathlib import Path
import json
from typing import Dict

from pathlib import Path
BASE_DIR  = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "exercises.json"

# Valeurs par défaut (avec muscles ajoutés)
DEFAULT_INVENTORY = {
    "Bench Press": {
        "type": "barbell",
        "increment": 5.0,
        "bar_weight": 45.0,
        "default_scheme": "4x5-7",
        "muscles": ["pectoraux", "triceps", "deltoïdes antérieurs"]
    },
    "Incline DB Press": {
        "type": "dumbbell",
        "increment": 5.0,
        "default_scheme": "3x8-12",
        "muscles": ["pectoraux supérieurs", "deltoïdes antérieurs", "triceps"]
    },
    "Back Squat": {
        "type": "barbell",
        "increment": 5.0,
        "bar_weight": 45.0,
        "default_scheme": "4x5-8",
        "muscles": ["quadriceps", "fessiers", "ischio-jambiers", "bas du dos", "abdominaux"]
    },
    "Leg Press": {
        "type": "machine",
        "increment": 10.0,
        "default_scheme": "3x10-15",
        "muscles": ["quadriceps", "fessiers", "ischio-jambiers"]
    },
    "Lat Pulldown": {
        "type": "machine",
        "increment": 5.0,
        "default_scheme": "3x8-12",
        "muscles": ["grand dorsal", "biceps", "rhomboïdes", "trapèzes"]
    },
    # Ajoute tes autres exercices ici avec leurs muscles
}


def load_inventory() -> Dict:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_INVENTORY, f, indent=2, ensure_ascii=False)
        return DEFAULT_INVENTORY.copy()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_INVENTORY.copy()


def save_inventory(inventory: Dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)


def add_exercise(name: str, ex_type: str, increment: float, bar_weight: float = 45.0, default_scheme: str = "3x8-12", muscles: list = None):
    inv = load_inventory()
    inv[name] = {
        "type": ex_type,
        "increment": increment,
        "bar_weight": bar_weight if ex_type == "barbell" else 0.0,
        "default_scheme": default_scheme,
        "muscles": muscles or []  # Liste vide par défaut
    }
    save_inventory(inv)
    print(f"✅ '{name}' ajouté/mis à jour")