# log_workout.py
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from progression import should_increase, next_weight, progression_status, parse_reps, estimate_1rm
from inventory import load_inventory, add_exercise   # ← NOUVEAU

DATA_FILE = Path("data/weights.json")

# load_weights, save_weights restent identiques (je les garde pour ne rien casser)

def load_weights() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"sessions": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {"sessions": {}}
    except:
        return {"sessions": {}}

def save_weights(weights: Dict[str, Any]):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde : {e}")

def log_single_exercise(exercise: str, weights: Dict[str, Any]) -> Dict[str, Any]:
    data = weights.copy() if isinstance(weights, dict) else {}

    print(f"\n{'─' * 65}")
    print(f"📌 {exercise}")

    # === AFFICHAGE DERNIÈRE SÉANCE (inchangé) ===
    last = data.get(exercise, {})
    if last and "history" in last and last["history"]:
        last_entry = last["history"][0]
        print(f"   Dernière : {last_entry['weight']} lbs | {last_entry['reps']} | {last_entry.get('note','—')}")

    # === NOUVELLE LOGIQUE INVENTAIRE ===
    inv = load_inventory()
    ex_info = inv.get(exercise)

    if ex_info:
        ex_type = ex_info["type"]
        inc = ex_info["increment"]
        bar_w = ex_info.get("bar_weight", 45.0)
        print(f"   Type détecté : {ex_type} (incrément auto {inc} lbs)")
    else:
        print(f"   ⚠️ '{exercise}' pas encore dans l'inventaire (on va l'ajouter après)")
        ex_type = None
        inc = 5.0
        bar_w = 45.0

    skip = False
    total_weight = 0.0
    input_value = 0.0

    # Demande DIRECTEMENT le bon format grâce à l'inventaire
    if ex_type == "barbell":
        val = input(f"   Poids par côté (plaques seulement) → ").strip()
        if not val:
            skip = True
        else:
            val = val.replace(",", ".")
            side = float(val)
            total_weight = side * 2 + bar_w
            input_value = side
            print(f"   Total : {total_weight:.1f} lbs")

    elif ex_type == "dumbbell":
        val = input(f"   Poids par haltère → ").strip()
        if not val:
            skip = True
        else:
            val = val.replace(",", ".")
            per = float(val)
            total_weight = per * 2
            input_value = per
            print(f"   Total : {total_weight:.1f} lbs")

    else:
        val = input(f"   Poids total (machine etc.) → ").strip()
        if not val:
            skip = True
        else:
            val = val.replace(",", ".")
            total_weight = float(val)
            input_value = total_weight
            print(f"   Total : {total_weight:.1f} lbs")

    if skip:
        print("   Exercice passé")
        return data

    # Reps + progression + 1RM (inchangé)
    reps_input = input("\nReps par série (ex: 7,6,5,5) → ").strip()
    if not reps_input:
        print("   Exercice passé")
        return data

    reps_list = parse_reps(reps_input)
    reps_str = ",".join(map(str, reps_list))

    print(f"   {progression_status(reps_str, exercise)}")

    if should_increase(reps_str, exercise):
        new_weight = next_weight(exercise, total_weight)
        print(f"   ✅ Augmente → {new_weight:.1f} lbs")
    else:
        new_weight = total_weight
        print(f"   🔄 Même poids")

    print(f"   1RM estimé : {estimate_1rm(total_weight, reps_str)} lbs")

    # Sauvegarde historique + current (inchangé)
    note = f"+{new_weight - total_weight:.1f}" if should_increase(reps_str, exercise) else "stagné"
    history_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weight": round(total_weight, 1),
        "reps": reps_str,
        "note": note,
        "1rm": estimate_1rm(total_weight, reps_str)
    }

    if exercise not in data:
        data[exercise] = {"history": []}

    data[exercise].setdefault("history", []).insert(0, history_entry)
    data[exercise]["history"] = data[exercise]["history"][:20]

    data[exercise]["current_weight"] = round(new_weight, 1)
    data[exercise]["last_reps"] = reps_str
    data[exercise]["last_logged"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data[exercise]["input_type"] = ex_type or "machine"
    data[exercise]["input_value"] = round(input_value, 1)

    # Si l'exercice n'était pas dans l'inventaire → on l'ajoute automatiquement
    if not ex_info:
        print("\nAjout automatique à l'inventaire...")
        t = input("Type (barbell / dumbbell / machine) → ").strip().lower()
        inc_input = float(input("Incrément par défaut (ex: 5) → ") or 5.0)
        add_exercise(exercise, t, inc_input)

    return data

def show_exercise_history(exercise: str, weights: dict, max_entries: int = 8):
    data = weights.get(exercise)
    if not data or "history" not in data or not data["history"]:
        print(f"\nAucun historique pour {exercise} (pas encore logué).")
        return

    print(f"\nHistorique de {exercise} (plus récentes en haut) :")
    print("─" * 70)
    print(f"{'Date':<12} {'Poids total':<12} {'Reps':<15} {'Note':<10} {'1RM':<9} {'Input':<15}")
    print("─" * 70)

    for entry in data["history"][:max_entries]:
        date = entry["date"]
        weight = f"{entry['weight']:.1f} lbs"
        reps = entry["reps"]
        note = entry["note"] if entry["note"] else "—"
        onerm = f"{entry['1rm']:.1f} lbs" if entry.get("1rm") else "—"
        input_info = ""
        if "input_type" in data:
            if data["input_type"] == "barbell":
                input_info = f"{data['input_value']:.1f} par côté"
            elif data["input_type"] == "dumbbell":
                input_info = f"{data['input_value']:.1f} par haltère"

        print(f"{date:<12} {weight:<12} {reps:<15} {note:<10} {onerm:<9} {input_info:<15}")

    print("─" * 70)
    if len(data["history"]) > max_entries:
        print(f"... et {len(data['history']) - max_entries} plus anciennes")