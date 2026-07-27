name: Wekelijkse herkalibratie

# Draait elke maandag om 04:00 UTC, en kan altijd handmatig gestart worden
# via het tabblad Actions ("Run workflow").
on:
  schedule:
    - cron: "0 4 * * 1"
  workflow_dispatch:
    inputs:
      dagen:
        description: "Aantal dagen backtest"
        required: false
        default: "150"

permissions:
  contents: write

jobs:
  kalibreren:
    runs-on: ubuntu-latest
    timeout-minutes: 180

    steps:
      - name: Repository ophalen
        uses: actions/checkout@v4

      - name: Python klaarzetten
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Kalibratie draaien
        env:
          PYTHONPATH: bot
          PYTHONUNBUFFERED: "1"
        run: python3 bot/kalibratie.py "${{ github.event.inputs.dagen || '150' }}"

      - name: Uitvoer controleren voor we iets vastleggen
        run: |
          python3 - <<'EOF'
          import json, sys
          from pathlib import Path

          data = json.load(open("app_params.json"))
          steden = data.get("steden", {})
          if len(steden) < 45:
              sys.exit(f"Te weinig steden in het resultaat: {len(steden)}")

          for key, stad in steden.items():
              horizons = [h for h in ("0", "1", "2") if h in stad]
              if not horizons:
                  sys.exit(f"{key} heeft geen enkele horizon")
              for h in horizons:
                  p = stad[h]
                  if not (0.5 <= p["b"] <= 1.5):
                      sys.exit(f"{key} h{h}: richtingscoefficient b={p['b']} onwaarschijnlijk")
                  if p["res_q10"] > 0 or p["res_q90"] < 0:
                      sys.exit(f"{key} h{h}: band sluit nul niet in")

          js = Path("app_params.js").read_text()
          if not js.startswith("window.APP_PARAMS = ") or not js.rstrip().endswith(";"):
              sys.exit("app_params.js heeft niet de verwachte vorm")
          json.loads(js[len("window.APP_PARAMS = "):].rstrip().rstrip(";"))

          print(f"Controle geslaagd: {len(steden)} steden, bandfactor {data['band_factor']}")
          EOF

      - name: Service worker versie ophogen zodat telefoons de nieuwe cijfers pakken
        run: |
          python3 - <<'EOF'
          import re
          from pathlib import Path

          pad = Path("sw.js")
          tekst = pad.read_text()
          nieuw, aantal = re.subn(
              r'weerbot-v(\d+)',
              lambda m: f"weerbot-v{int(m.group(1)) + 1}",
              tekst,
          )
          if aantal:
              pad.write_text(nieuw)
              print(f"Service worker opgehoogd ({aantal} plek(ken))")
          EOF

      - name: Vastleggen als er iets veranderd is
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          if git diff --quiet -- app_params.js app_params.json sw.js; then
            echo "Geen wijzigingen, niets vast te leggen."
            exit 0
          fi
          git add app_params.js app_params.json sw.js
          git commit -m "Herkalibratie $(date -u +%Y-%m-%d)"
          git push
