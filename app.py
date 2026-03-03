# app.py

import sys
from datetime import date, datetime

from planner import get_today, get_week_schedule, get_suggested_weights_for_today, load_program, save_program
from hiit import get_hiit_str
from log_workout import load_weights, save_weights, log_single_exercise, show_exercise_history
from inventory import load_inventory, add_exercise
from user_profile import load_user_profile
from stats import generate_dashboard


START_DATE = date(2026, 3, 3)  # ← Change cette date si tu recommences un cycle

def get_current_week() -> int:
    """Retourne la semaine réelle du programme basée sur START_DATE."""
    delta = date.today() - START_DATE
    return max(1, (delta.days // 7) + 1)


class TrainingOSApp:

    def __init__(self):
        self.weights = load_weights()
        self.inventory = load_inventory()
        self.program = load_program()

    def clear_screen(self):
        print("\033[H\033[J", end="")

    def afficher_menu_principal(self):
        self.clear_screen()
        week = get_current_week()
        print("\n" + "═" * 60)
        print("      LET'S GO !!")
        print("═" * 60)
        print(f"Aujourd'hui : {datetime.now().strftime('%Y-%m-%d')} → {get_today()}  |  Semaine {week}")
        print()
        print("  1. Log ma séance d'aujourd'hui")
        print("  2. Voir les poids recommandés")
        print("  3. Planning de la semaine")
        print("  4. HIIT de la semaine")
        print("  5. Historique d'un exercice")
        print("  6. Voir notes/RPE des séances")
        print("  7. Gérer l'inventaire des exercices")
        print("  8. Modifier le programme hebdomadaire")
        print("  9. Configurer / modifier mon profil")
        print(" 10. Voir mon récap intelligent")
        print(" 11. Voir catalogue des exercices")
        print(" 12. 📊 Dashboard stats (navigateur)")
        print(" 13. 🏃 Historique HIIT")
        print("  0. Quitter")
        print("═" * 60)
        print()

    def run(self):
        while True:
            self.afficher_menu_principal()
            choix = input("Ton choix (0-13) → ").strip().lower()

            if choix == "1":
                self.log_seance_aujourdhui()
            elif choix == "2":
                self.voir_poids_recommandes()
            elif choix == "3":
                self.afficher_planning_semaine()
            elif choix == "4":
                self.voir_hiit_semaine()
            elif choix == "5":
                self.voir_historique_exercice()
            elif choix == "6":
                self.voir_notes_seances()
            elif choix == "7":
                self.gerer_inventaire()
            elif choix == "8":
                self.modifier_programme()
            elif choix == "9":
                self.setup_or_edit_profile()
            elif choix == "10":
                self.show_recap_intelligent()
            elif choix == "11":
                self.voir_catalogue_exercices()
            elif choix == "12":
                self.voir_dashboard_stats()
            elif choix == "13":
                self.voir_historique_hiit()
            elif choix in ("0", "q", "quit", "exit"):
                print("\nGarde la promesse que tu t'es fait à toi même, lock n loaded !\n")
                sys.exit(0)
            else:
                print("Choix invalide – essaie 0 à 12.")

            input("\nAppuie sur Entrée pour revenir au menu...")

    # ────────────────────────────────────────────────

    def log_seance_aujourdhui(self):
        today_session = get_today()
        today_date = datetime.now().strftime('%Y-%m-%d')

        print(f"\n{'═' * 70}")
        print(f"  SÉANCE DU {today_date} → {today_session}")
        print(f"{'═' * 70}\n")

        suggestions = get_suggested_weights_for_today(self.weights)
        if suggestions:
            print("POIDS RECOMMANDÉS POUR AUJOURD'HUI :")
            for item in suggestions:
                print(f"  {item['exercise']:<25} {item['display']}")
            print()

        if "HIIT" in today_session or today_session in ["Yoga", "Recovery"]:
            if "HIIT" in today_session:
                week = get_current_week()
                print(f"🏃 HIIT DU JOUR  (Semaine {week})\n   " + get_hiit_str(week))
                reponse = input("\nAs-tu fait ton HIIT ? (o/n) → ").strip().lower()
                if reponse in ("o", "oui", "y", "yes"):
                    from log_workout import log_hiit_session
                    log_hiit_session(week)
            else:
                emoji = "🧘" if today_session == "Yoga" else "😴"
                print(f"{emoji} Jour de {today_session.lower()} – récupération")
            input("\nAppuie Entrée pour continuer...")
            return

        if today_session not in self.program:
            print("Aucun programme défini pour ce jour.")
            return

        exercises = list(self.program[today_session].keys())
        print(f"Exercices prévus ({len(exercises)}) :")
        for i, ex in enumerate(exercises, 1):
            print(f"  {i:2}. {ex}")
        print()

        reponse = input("As-tu fait ta séance aujourd'hui ? (o/n) ").strip().lower()
        if reponse not in ("o", "oui", "y", "yes"):
            print("OK, à demain ! 💪")
            return

        print("\nC'est parti...\n")

        faits = 0
        for exercise in exercises:
            self.weights = log_single_exercise(exercise, self.weights)
            if exercise in self.weights and self.weights[exercise].get("last_logged", "").startswith(today_date):
                faits += 1

        if faits > 0:
            save_weights(self.weights)
            print(f"\n{faits} exos enregistrés – super boulot ! 🔥")

        rpe_str = input("\nRPE global (1-10, Entrée=skip) → ").strip()
        rpe = int(rpe_str) if rpe_str.isdigit() and 1 <= int(rpe_str) <= 10 else None
        comment = input("Commentaire / ressenti (Entrée=rien) → ").strip()

        if rpe or comment:
            if "sessions" not in self.weights:
                self.weights["sessions"] = {}
            self.weights["sessions"][today_date] = {
                "rpe": rpe,
                "comment": comment,
                "exos": exercises
            }
            save_weights(self.weights)
            print("Note séance sauvegardée ✓")

        profile = load_user_profile()
        goal = profile.get("goal", "force")

        print("\n" + "─" * 50)
        if goal == "force":
            print("   Objectif force activé : continue à pousser les charges !")
            if faits > 0:
                print("   +5 lbs ou + reps sur un gros lift ? T'es sur la voie royale 💪")
        elif goal == "hypertrophie":
            print("   Objectif hypertrophie : bon volume – garde la tension musculaire !")
            print("   Pense à bien manger après, c'est là que ça se construit 🔥")
        elif goal == "perte de poids":
            print("   Objectif perte de poids : séance solide – continue le déficit calorique malin")
            print("   Hydrate-toi bien et protège tes articulations !")
        elif goal == "recomposition":
            print("   Objectif recomposition : équilibre parfait entre force et esthétique")
            print("   T'as bien géré – prot et glucides post-entraînement !")
        else:
            print("   Objectif non défini – mets-le dans ton profil (option 9) !")

        if today_session in ["Upper A", "Upper B"]:
            print("   Jour Upper : tes pecs, dos et épaules te remercient déjà !")
        elif today_session == "Lower":
            print("   Jour Lower : jambes et fessiers en feu – t'as tout donné !")
        print("─" * 50)

    def voir_poids_recommandes(self):
        suggestions = get_suggested_weights_for_today(self.weights)
        if not suggestions:
            print("\nAucune suggestion aujourd'hui.\n")
            return
        print("\nPOIDS RECOMMANDÉS :")
        print("-" * 70)
        for item in suggestions:
            print(f"  {item['exercise']:<25} → {item['display']}")
        print("-" * 70)

    def afficher_planning_semaine(self):
        schedule = get_week_schedule()
        today = get_today()
        week = get_current_week()
        print(f"\nPLANNING SEMAINE {week}")
        print("-" * 40)
        for d, s in schedule.items():
            marker = " ◀ AUJOURD'HUI" if s == today else ""
            print(f"  {d} → {s}{marker}")
        print("-" * 40)

    def voir_hiit_semaine(self):
        week = get_current_week()
        print(f"\nHIIT SEMAINE {week} : {get_hiit_str(week)}")

    def voir_historique_exercice(self):
        exo = input("\nExercice à voir → ").strip()
        if not exo:
            return
        found = False
        for key in self.weights:
            if exo.lower() in key.lower() and key != "sessions":
                show_exercise_history(key, self.weights)
                found = True
                break
        if not found:
            print("Exercice non trouvé.")

    def voir_notes_seances(self):
        sessions = self.weights.get("sessions", {})
        if not sessions:
            print("Aucune note enregistrée pour l'instant.")
            return
        print("\nNOTES / RPE DES DERNIÈRES SÉANCES")
        print("-" * 60)
        for date_key in sorted(sessions.keys(), reverse=True)[:10]:
            s = sessions[date_key]
            rpe_txt = f"RPE {s['rpe']}" if s.get('rpe') else "—"
            print(f"{date_key} | {rpe_txt} | {s.get('comment', '—')}")
        print("-" * 60)

    def gerer_inventaire(self):
        while True:
            print("\n" + "═" * 50)
            print("   GESTION INVENTAIRE DES EXERCICES")
            print("═" * 50)
            inv = load_inventory()
            if inv:
                print("Exercices actuels :")
                for ex, info in sorted(inv.items()):
                    bar = f" (barre {info.get('bar_weight', 45)} lbs)" if info["type"] == "barbell" else ""
                    scheme = info.get("default_scheme", "—")
                    print(f"  • {ex:<22} ({info['type']}, +{info['increment']} lbs, scheme: {scheme}{bar})")
            else:
                print("Aucun exercice pour l'instant.")

            print("\nOptions :")
            print("  1. Ajouter / modifier un exercice")
            print("  0. Retour au menu principal")
            print("═" * 50)

            choix = input("Ton choix → ").strip().lower()

            if choix in ("0", "back", "b", "retour"):
                break

            if choix == "1":
                name = input("Nom de l'exercice → ").strip()
                if not name:
                    continue
                t = input("Type (barbell / dumbbell / machine / autre) → ").strip().lower()
                inc_str = input("Incrément par défaut → ").strip()
                inc = float(inc_str) if inc_str.replace('.', '', 1).isdigit() else 5.0
                scheme = input("Scheme par défaut (ex: 4x5-7) → ").strip() or "3x8-12"
                muscles_input = input("Muscles ciblés (séparés par virgule) → ").strip()
                muscles = [m.strip() for m in muscles_input.split(",") if m.strip()] if muscles_input else []
                bar_w = 45.0
                if t == "barbell":
                    bar_str = input("Poids barre (défaut 45) → ").strip()
                    bar_w = float(bar_str) if bar_str.replace('.', '', 1).isdigit() else 45.0
                add_exercise(name, t, inc, bar_w, scheme, muscles)
            else:
                print("Choix invalide.")

    def modifier_programme(self):
        while True:
            print("\n" + "═" * 50)
            print("   MODIFIER LE PROGRAMME HEBDOMADAIRE")
            print("═" * 50)
            print(f"Jours disponibles : {list(self.program.keys())}")
            jour = input("Jour (Upper A / Upper B / Lower) ou 0/back → ").strip()

            if jour.lower() in ("0", "back", "b", "retour"):
                break

            if jour not in self.program:
                print(f"Jour '{jour}' non trouvé.")
                continue

            print(f"\nExercices pour {jour} :")
            for ex, sch in self.program[jour].items():
                print(f"  • {ex:<22} {sch}")

            print("\nActions :")
            print("  1. Ajouter un exercice")
            print("  2. Enlever un exercice")
            print("  3. Changer scheme")
            print("  0. Retour")
            print("═" * 50)

            action = input("Choix → ").strip().lower()

            if action in ("0", "back", "b", "retour"):
                continue

            if action == "1":
                exo = input("Exercice à ajouter → ").strip()
                if exo:
                    inv_info = load_inventory().get(exo)
                    if not inv_info:
                        print(f"⚠️ '{exo}' pas dans l'inventaire (ajoute-le via option 7 d'abord).")
                        continue
                    scheme = input(f"Scheme (défaut {inv_info.get('default_scheme', '3x8-12')}) → ").strip() or inv_info.get('default_scheme', '3x8-12')
                    self.program[jour][exo] = scheme
                    save_program(self.program)
                    print(f"✅ '{exo}' ajouté à {jour} !")

            elif action == "2":
                exo = input("Exercice à enlever → ").strip()
                if exo in self.program[jour]:
                    del self.program[jour][exo]
                    save_program(self.program)
                    print(f"✅ '{exo}' retiré de {jour}.")
                else:
                    print(f"'{exo}' non trouvé dans {jour}.")

            elif action == "3":
                exo = input("Exercice à modifier → ").strip()
                if exo in self.program[jour]:
                    new_scheme = input(f"Nouveau scheme (actuel: {self.program[jour][exo]}) → ").strip()
                    if new_scheme:
                        self.program[jour][exo] = new_scheme
                        save_program(self.program)
                        print(f"✅ Scheme mis à jour !")
                else:
                    print(f"'{exo}' non trouvé dans {jour}.")
            else:
                print("Action non reconnue.")

    def setup_or_edit_profile(self):
        from user_profile import setup_user_profile
        setup_user_profile()
        self.user_profile = load_user_profile()

    def show_recap_intelligent(self):
        print("\n" + "═" * 60)
        print("   RÉCAP PERSONNALISÉ")
        print("═" * 60)

        profile = load_user_profile()
        print(f"Profil : {profile['name'] or 'Vince'}, {profile['age'] or '?'} ans, "
              f"{profile['level']} – Objectif : {profile['goal']}")
        print(f"Unités : {profile['units']}  |  Semaine du programme : {get_current_week()}")

        big_lifts = ["Bench Press", "Back Squat", "Romanian Deadlift", "Overhead Press"]
        print("\nProgression 1RM (estimée) – derniers logs :")
        for lift in big_lifts:
            if lift in self.weights and self.weights[lift].get("history"):
                latest = self.weights[lift]["history"][0]
                print(f"  {lift:<20} {latest['1rm']:.1f} lbs ({latest['date']})")
            else:
                print(f"  {lift:<20} pas encore logué")

        print("\nExos stagnants (même poids ≥ 3 séances) :")
        stagnants = []
        for ex, data in self.weights.items():
            if ex == "sessions":
                continue
            hist = data.get("history", [])
            if len(hist) >= 3:
                last3_weights = [e["weight"] for e in hist[:3]]
                if len(set(last3_weights)) == 1:
                    stagnants.append(f"{ex} ({last3_weights[0]} lbs ×3)")
        if stagnants:
            print("  " + "\n  ".join(stagnants))
            print("   → Suggestion : deload 10-15% ou changer scheme")
        else:
            print("  Aucun exo stagné récemment – continue le grind ! 🔥")

        print("\nRécap global :")
        sessions = self.weights.get("sessions", {})
        if sessions:
            last_date = max(sessions.keys())
            last_rpe = sessions[last_date].get("rpe", "—")
            print(f"  Dernière séance : {last_date} (RPE {last_rpe})")
        else:
            print("  Pas encore de séances loguées.")

        print("═" * 60)

    def voir_catalogue_exercices(self):
        print("\n" + "═" * 70)
        print("   CATALOGUE DES EXERCICES (Inventaire complet)")
        print("═" * 70)

        inv = load_inventory()
        if not inv:
            print("Aucun exercice dans l'inventaire pour l'instant.")
            return

        for ex, info in sorted(inv.items()):
            muscles = ", ".join(info.get("muscles", [])) or "non spécifié"
            bar = f" (barre {info.get('bar_weight', 45)} lbs)" if info["type"] == "barbell" else ""
            print(f"  • {ex:<25}")
            print(f"    Type: {info['type']:<12} Incrément: +{info['increment']} lbs{bar}")
            print(f"    Scheme défaut: {info.get('default_scheme', '—')}")
            print(f"    Muscles ciblés: {muscles}")
            print("─" * 70)

    def voir_dashboard_stats(self):
        generate_dashboard()

    def voir_historique_hiit(self):
        from log_workout import show_hiit_history
        show_hiit_history()