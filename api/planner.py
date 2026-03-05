# planner.py
from datetime import datetime
import json
from pathlib import Path

from progression import should_increase, next_weight

from pathlib import Path
BASE_DIR     = Path(__file__).parent
PROGRAM_FILE = BASE_DIR / "data" / "program.json"

# Valeurs par défaut si le fichier n'existe pas encore
DEFAULT_PROGRAM = {
    "Upper A": {
        "Bench Press":      "4x5-7",
        "Barbell Row":      "4x6-8",
        "Incline DB Press": "3x8-10",
        "Lat Pulldown":     "3x8-10",
        "Overhead Press":   "3x6-8"
    },
    "Upper B": {
        "Incline DB Press":  "4x8-10",
        "T-Bar Row":         "4x8-10",
        "DB Bench Press":    "3x10-12",
        "Seated Row":        "3x10-12",
        "Lateral Raises":    "4x12-15",
        "Triceps Extension": "3x10-12",
        "Hammer Curl":       "3x10-12",
        "Face Pull":         "3x15"
    },
    "Lower": {
        "Back Squat":        "4x5-7",
        "Leg Press":         "3x10-12",
        "Leg Curl":          "3x10-12",
        "Romanian Deadlift": "3x8-10",
        "Calf Raise":        "3x12-15",
        "Abs":               "3x12-15"
    }
}

SCHEDULE = {
    0: "Upper A", 1: "HIIT 1", 2: "Upper B", 3: "HIIT 2", 4: "Lower", 5: "Yoga", 6: "Recovery"
}


from pathlib import Path
from typing import Dict, Any
import json

# Définition du chemin absolu (remonte depuis api/ → racine projet → data/)
PROGRAM_FILE = Path(__file__).parent.parent / "data" / "program.json"

# Ton DEFAULT_PROGRAM (à définir ici ou importé d'un autre fichier)
# Exemple minimal – remplace par le vrai contenu par défaut de ton programme
DEFAULT_PROGRAM = {
    "Lundi": {"Squat": "5x5", "Bench Press": "5x5"},
    "Mardi": {"Deadlift": "1x5", "Overhead Press": "5x5"},
    # ... ajoute tous tes jours et exercices par défaut
}


def load_program() -> Dict[str, Any]:
    """
    Charge program.json de façon sûre.
    - Crée le fichier avec DEFAULT_PROGRAM s'il n'existe pas
    - Retourne une copie de DEFAULT_PROGRAM en cas d'erreur
    - Loggue les problèmes pour debug Vercel
    """
    if not PROGRAM_FILE.is_file():
        PROGRAM_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            PROGRAM_FILE.write_text(
                json.dumps(DEFAULT_PROGRAM, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            print(f"[INFO] Fichier program.json créé avec valeurs par défaut : {PROGRAM_FILE}")
            return DEFAULT_PROGRAM.copy()
        except Exception as e:
            print(f"[ERROR] Impossible de créer {PROGRAM_FILE} : {e}")
            return DEFAULT_PROGRAM.copy()

    try:
        data = json.loads(PROGRAM_FILE.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            print(f"[WARNING] Contenu invalide dans {PROGRAM_FILE} : pas un dictionnaire")
            return DEFAULT_PROGRAM.copy()

        return data

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON corrompu dans {PROGRAM_FILE} : {e}")
        return DEFAULT_PROGRAM.copy()

    except Exception as e:
        print(f"[ERROR] Erreur chargement {PROGRAM_FILE} : {e}")
        return DEFAULT_PROGRAM.copy()


def save_program(program: dict):
    try:
        with open(PROGRAM_FILE, "w", encoding="utf-8") as f:
            json.dump(program, f, indent=2, ensure_ascii=False)
        print("Programme sauvegardé ✓")
    except Exception as e:
        print(f"Erreur sauvegarde programme : {e}")


# Charge une fois au démarrage du module
#PROGRAM = load_program()


def get_today() -> str:
    return SCHEDULE[datetime.today().weekday()]


def get_week_schedule() -> dict:
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    return {days[i]: SCHEDULE[i] for i in range(7)}


def get_suggested_weights_for_today(weights: dict) -> list[dict]:
    today_session = get_today()
    program = load_program()  # ← recharge depuis le fichier

    if today_session not in program:
        return []

    result = []
    for exercise in program[today_session]:
        data = weights.get(exercise, {})
        current_total = data.get("current_weight", data.get("weight", 0.0))
        last_reps = data.get("last_reps", "")
        input_type = data.get("input_type", "total")

        suggested = current_total
        if should_increase(last_reps, exercise):
            suggested = next_weight(exercise, current_total)

        if input_type == "barbell":
            side = (suggested - 45) / 2 if suggested >= 45 else 0
            display = f"{side:.1f} par côté (total {suggested:.1f} lbs)"
        elif input_type == "dumbbell":
            display = f"{suggested/2:.1f} par haltère (total {suggested:.1f} lbs)"
        else:
            display = f"{suggested:.1f} lbs total"

        result.append({'exercise': exercise, 'display': display})
    return result