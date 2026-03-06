import requests
from db import set_json

# Ta clé API
HEADERS = {
    "X-RapidAPI-Key": "35105723d4msh22056a747ded06ap1784e0jsnda9b2359112f",
    "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
}


def import_with_url_construction(limit=100):
    print(f"Extraction de {limit} exercices (Méthode Reconstruction URL)...")
    url_list = "https://exercisedb.p.rapidapi.com/exercises"

    try:
        response = requests.get(url_list, headers=HEADERS, params={"limit": limit})
        exercises = response.json()
        new_inventory = {}

        for item in exercises:
            exo_id = item.get('id')
            name = item.get('name', 'Unknown').title()

            # --- LA MAGIE : On construit l'URL directement ---
            # L'ID doit être sur 4 chiffres (ex: 1 -> 0001)
            formatted_id = str(exo_id).zfill(4)
            gif_url = f"https://edb-4059a1.c.cdn77.org/exercises/{formatted_id}.gif"

            # --- Logique de catégorie ---
            body_part = item.get('bodyPart', '').lower()
            category = 'legs'
            if body_part in ['chest', 'shoulders', 'triceps']:
                category = 'push'
            elif body_part in ['back', 'upper back', 'biceps']:
                category = 'pull'
            elif body_part in ['waist', 'abs']:
                category = 'core'

            new_inventory[name] = {
                "type": item.get('equipment', 'other').replace(" ", ""),
                "increment": 5.0,
                "bar_weight": 45.0 if item.get('equipment') == 'barbell' else 0.0,
                "default_scheme": "3x8-12",
                "muscles": [item.get('target', 'n/a')],
                "tips": ". ".join(item.get('instructions', [])[:2]),
                "category": category,
                "gif_url": gif_url
            }
            print(f"✅ {name} (ID:{formatted_id}) généré !")

        if new_inventory:
            set_json("inventory", new_inventory)
            print(f"\n🚀 Succès ! {len(new_inventory)} exercices configurés avec URLs de GIFs.")

    except Exception as e:
        print(f"Erreur : {e}")


if __name__ == "__main__":
    import_with_url_construction(100)