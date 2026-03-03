# stats.py
import json
import webbrowser
import tempfile
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DATA_FILE = Path("data/weights.json")


def load_weights() -> dict:
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_volume_par_seance(weights: dict) -> list[dict]:
    """Volume total par date : somme(poids × reps) pour tous les exos loggués ce jour."""
    volume_par_date = defaultdict(float)

    for ex, data in weights.items():
        if ex == "sessions":
            continue
        for entry in data.get("history", []):
            date = entry.get("date", "")
            w = entry.get("weight", 0)
            reps_str = entry.get("reps", "")
            try:
                reps_list = [int(r) for r in reps_str.split(",") if r.strip()]
                volume = w * sum(reps_list)
                volume_par_date[date] += volume
            except:
                continue

    return [{"date": d, "volume": round(v, 1)}
            for d, v in sorted(volume_par_date.items())]


def compute_frequence_par_semaine(weights: dict) -> list[dict]:
    """Nombre de séances distinctes par semaine."""
    seances_par_semaine = defaultdict(set)

    for ex, data in weights.items():
        if ex == "sessions":
            continue
        for entry in data.get("history", []):
            date_str = entry.get("date", "")
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d")
                semaine = d.strftime("%Y-S%W")
                seances_par_semaine[semaine].add(date_str)
            except:
                continue

    return [{"semaine": s, "seances": len(days)}
            for s, days in sorted(seances_par_semaine.items())]


def compute_volume_par_semaine(volume_par_seance: list[dict]) -> list[dict]:
    """Regroupe le volume par semaine pour la comparaison."""
    volume_semaine = defaultdict(float)

    for entry in volume_par_seance:
        try:
            d = datetime.strptime(entry["date"], "%Y-%m-%d")
            semaine = d.strftime("%Y-S%W")
            volume_semaine[semaine] += entry["volume"]
        except:
            continue

    return [{"semaine": s, "volume": round(v, 1)}
            for s, v in sorted(volume_semaine.items())]


def generate_dashboard():
    weights = load_weights()

    if not weights or all(k == "sessions" for k in weights):
        print("\nPas encore assez de données pour générer des stats.")
        print("Logge quelques séances d'abord ! 💪")
        return

    volume_seance = compute_volume_par_seance(weights)
    frequence = compute_frequence_par_semaine(weights)
    volume_semaine = compute_volume_par_semaine(volume_seance)

    # Données JS
    vol_dates   = [e["date"]    for e in volume_seance]
    vol_vals    = [e["volume"]  for e in volume_seance]
    freq_labels = [e["semaine"] for e in frequence]
    freq_vals   = [e["seances"] for e in frequence]
    vsem_labels = [e["semaine"] for e in volume_semaine]
    vsem_vals   = [e["volume"]  for e in volume_semaine]

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>TrainingOS – Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Segoe UI', sans-serif;
      background: #0f0f13;
      color: #e0e0e0;
      padding: 30px;
    }}
    h1 {{
      text-align: center;
      font-size: 2rem;
      color: #f97316;
      margin-bottom: 6px;
      letter-spacing: 2px;
    }}
    .subtitle {{
      text-align: center;
      color: #666;
      margin-bottom: 40px;
      font-size: 0.9rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }}
    .card {{
      background: #1a1a24;
      border: 1px solid #2a2a3a;
      border-radius: 12px;
      padding: 24px;
    }}
    .card.wide {{
      grid-column: span 2;
    }}
    .card h2 {{
      font-size: 1rem;
      color: #f97316;
      margin-bottom: 20px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    canvas {{ width: 100% !important; }}
  </style>
</head>
<body>
  <h1>💪 TRAININGOS</h1>
  <p class="subtitle">Dashboard de performance – généré le {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

  <div class="grid">

    <div class="card wide">
      <h2>📊 Volume total par séance (lbs × reps)</h2>
      <canvas id="volumeSeance"></canvas>
    </div>

    <div class="card">
      <h2>📅 Fréquence par semaine (nb séances)</h2>
      <canvas id="frequence"></canvas>
    </div>

    <div class="card">
      <h2>📈 Volume total par semaine</h2>
      <canvas id="volumeSemaine"></canvas>
    </div>

  </div>

  <script>
    const orange = '#f97316';
    const blue   = '#3b82f6';
    const green  = '#22c55e';

    const defaults = {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#222' }} }},
        y: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#222' }} }}
      }}
    }};

    // Volume par séance
    new Chart(document.getElementById('volumeSeance'), {{
      type: 'bar',
      data: {{
        labels: {vol_dates},
        datasets: [{{
          data: {vol_vals},
          backgroundColor: orange + '99',
          borderColor: orange,
          borderWidth: 1,
          borderRadius: 4
        }}]
      }},
      options: {{ ...defaults }}
    }});

    // Fréquence par semaine
    new Chart(document.getElementById('frequence'), {{
      type: 'bar',
      data: {{
        labels: {freq_labels},
        datasets: [{{
          data: {freq_vals},
          backgroundColor: blue + '99',
          borderColor: blue,
          borderWidth: 1,
          borderRadius: 4
        }}]
      }},
      options: {{ ...defaults }}
    }});

    // Volume par semaine
    new Chart(document.getElementById('volumeSemaine'), {{
      type: 'line',
      data: {{
        labels: {vsem_labels},
        datasets: [{{
          data: {vsem_vals},
          borderColor: green,
          backgroundColor: green + '22',
          borderWidth: 2,
          pointBackgroundColor: green,
          pointRadius: 5,
          fill: true,
          tension: 0.3
        }}]
      }},
      options: {{ ...defaults }}
    }});
  </script>
</body>
</html>"""

    # Sauvegarde et ouvre dans le navigateur
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False,
        encoding="utf-8", prefix="trainingOS_stats_"
    )
    tmp.write(html)
    tmp.close()

    webbrowser.open(f"file://{tmp.name}")
    print(f"\n✅ Dashboard ouvert dans ton navigateur !")
    print(f"   Fichier : {tmp.name}")