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


def calculate_plates(target_weight, bar_weight=45.0):
    if not target_weight or target_weight <= bar_weight:
        return []

    weight_per_side = (target_weight - bar_weight) / 2
    plates = [45, 35, 25, 10, 5, 2.5]
    needed_plates = []

    # Utiliser round(..., 2) évite que 2.5 devienne 2.49999999
    temp_weight = round(float(weight_per_side), 2)

    for plate in plates:
        while temp_weight >= plate:
            needed_plates.append(plate)
            temp_weight = round(temp_weight - plate, 2)

    return needed_plates

from pathlib import Path
from typing import Dict, Any
import json

# Définition du chemin (même logique que pour weights.json)
# Remonte de api/ → racine projet → data/
INVENTORY_FILE = Path(__file__).parent.parent / "data" / "inventory.json"

# Ton DEFAULT_INVENTORY (à définir quelque part – ici en exemple)
DEFAULT_INVENTORY = {
    "Squat": {"type": "barbell", "increment": 5, "bar_weight": 45},
    "Bench Press": {"type": "barbell", "increment": 5, "bar_weight": 45},
    # ... ajoute tous tes exercices par défaut
}


def load_inventory() -> Dict[str, Any]:
    """
    Charge inventory.json de façon sûre.
    - Crée le fichier avec DEFAULT_INVENTORY s'il n'existe pas
    - Retourne une copie de DEFAULT_INVENTORY en cas d'erreur
    - Loggue les problèmes pour debug Vercel
    """
    if not INVENTORY_FILE.is_file():
        INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            INVENTORY_FILE.write_text(
                json.dumps(DEFAULT_INVENTORY, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            print(f"[INFO] Fichier créé : {INVENTORY_FILE}")
            return DEFAULT_INVENTORY.copy()
        except Exception as e:
            print(f"[ERROR] Impossible de créer {INVENTORY_FILE} : {e}")
            return DEFAULT_INVENTORY.copy()

    try:
        data = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            print(f"[WARNING] Contenu invalide dans {INVENTORY_FILE} : pas un dict")
            return DEFAULT_INVENTORY.copy()

        return data

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON corrompu dans {INVENTORY_FILE} : {e}")
        return DEFAULT_INVENTORY.copy()

    except Exception as e:
        print(f"[ERROR] Erreur chargement {INVENTORY_FILE} : {e}")
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