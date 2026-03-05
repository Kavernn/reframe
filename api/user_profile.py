from __future__ import annotations
from datetime import datetime
from .db import get_json, set_json

KEY = "user"

DEFAULT_USER = {
    "name": "Vince",
    "age": None,
    "weight_kg": None,
    "height_cm": None,
    "sex": None,              # "m" ou "f"
    "level": "intermédiaire", # débutant / intermédiaire / avancé
    "goal": "force",          # force / hypertrophie / perte de poids / recomposition
    "units": "lbs",           # lbs ou kg
    "created": datetime.now().isoformat(),
    "last_updated": None,
}

def load_user_profile() -> dict:
    """
    Lit le profil depuis Supabase KV ("user").
    Si absent, retourne DEFAULT_USER.
    """
    data = get_json(KEY, {}) or {}
    if not isinstance(data, dict) or not data:
        return DEFAULT_USER.copy()
    return data

def save_user_profile(profile: dict):
    profile["last_updated"] = datetime.now().isoformat()
    set_json(KEY, profile)

def setup_user_profile():
    """Questionnaire rapide (CLI) puis sauvegarde dans KV."""
    profile = load_user_profile()
    print("\n" + "═" * 50)
    print(" CONFIGURATION PROFIL PERSONNEL")
    print("═" * 50)
    print("Pour te donner des conseils plus adaptés, remplis ces infos (tu peux skip avec Entrée)\n")

    from .menu_select import selectionner

    profile["name"] = input(f"Prénom / surnom (actuel: {profile['name']}) → ").strip() or profile["name"]
    profile["age"] = input(f"Âge (actuel: {profile['age'] or '?'}) → ").strip() or profile["age"]
    profile["weight_kg"] = input(f"Poids actuel (kg) (actuel: {profile['weight_kg'] or '?'}) → ").strip() or profile["weight_kg"]
    profile["height_cm"] = input(f"Taille (cm) (actuel: {profile['height_cm'] or '?'}) → ").strip() or profile["height_cm"]

    sex = selectionner("Sexe :", ["m", "f"])
    profile["sex"] = sex or profile["sex"]

    level = selectionner("Niveau :", ["débutant", "intermédiaire", "avancé"])
    profile["level"] = level or profile["level"]

    goal = selectionner("Objectif principal :", ["force", "hypertrophie", "perte de poids", "recomposition"])
    profile["goal"] = goal or profile["goal"]

    units = selectionner("Unités préférées :", ["lbs", "kg"])
    profile["units"] = units or profile["units"]

    save_user_profile(profile)
    print("\nProfil sauvegardé ! Ton assistant est maintenant personnalisé 💪")