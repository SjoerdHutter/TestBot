#!/usr/bin/env python3
"""
Backfill van Open-Meteo per stad, 2021-01-01 tot en met gisteren.

Per (stad, datum) worden verzameld, opgeslagen in graden Celsius:
  era5_max     ERA5(T) reanalyse daghoogste  (waarneming-proxy op het gridpunt)
  d0_<model>   dag-0 archief van de historical-forecast-api (kortste lead, ~analyse)
  p1_<model>   echte forecast met 1 dag lead (previous-runs, uurmax over de lokale dag)
  p2_<model>   idem met 2 dagen lead

Modellen: ecmwf_ifs025, ecmwf_aifs025, gfs_seamless, icon_seamless, gem_seamless.
Archiefdiepte verschilt per model; wat ontbreekt blijft leeg.

Gebruik:
  python3 backfill_openmeteo.py fetch    # haalt alles op (hervatbaar, cache in cache/)
  python3 backfill_openmeteo.py build    # bouwt CSV's uit de cache naar uit/
Alleen stdlib. Bundelt 17 steden per aanroep en wacht netjes bij HTTP 429.
"""

import csv
import hashlib
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import date, timedelta
from pathlib import Path

HIER   = Path(__file__).parent
CACHE  = HIER / "cache"
INDEX  = HIER / "cache_index.json"
UIT    = HIER / "uit"
STEDEN = json.load(open(HIER / "steden.json"))

MODELLEN   = ["ecmwf_ifs025", "ecmwf_aifs025", "ecmwf_aifs025_single",
              "gfs_seamless", "icon_seamless", "gem_seamless"]
DAG0_BASIS = ["ecmwf_ifs025", "ecmwf_aifs025", "gfs_seamless", "icon_seamless", "gem_seamless"]
BEGIN_JAAR = 2021
EIND_DATUM = (date.today() - timedelta(days=1)).isoformat()
BUNDEL     = 17          # steden per aanroep
PAUZE      = 2.5         # seconden tussen aanroepen

# Archiefstart per model bij de previous-runs API (gepeild 2026-07-29).
PREV_START = {"gfs_seamless": 2021, "icon_seamless": 2024, "gem_seamless": 2024,
              "ecmwf_ifs025": 2024, "ecmwf_aifs025": 2024,
              "ecmwf_aifs025_single": 2025}   # opvolger van aifs025 vanaf feb 2025

# ── HTTP met herkansing en cache ─────────────────────────────────────────────

def _haal(url: str, pogingen: int = 5):
    for p in range(pogingen):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "weerbot-backfill/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wacht = 10 * (p + 1)
                print(f"      HTTP {e.code}, {wacht}s wachten...", flush=True)
                time.sleep(wacht)
                continue
            raise
        except Exception:
            if p == pogingen - 1:
                raise
            time.sleep(6 * (p + 1))
    raise RuntimeError("opgegeven na herhaald HTTP 429")


def _index_lees() -> dict:
    return json.loads(INDEX.read_text()) if INDEX.exists() else {}

def _index_schrijf(idx: dict):
    INDEX.write_text(json.dumps(idx))

def gecachet(url: str, label: str, meta: dict):
    """Antwoord + betekenis (bron, modellen, stedengroep) op schijf bewaren."""
    CACHE.mkdir(exist_ok=True)
    naam = hashlib.sha1(url.encode()).hexdigest()[:20] + ".json"
    pad  = CACHE / naam
    idx  = _index_lees()
    if pad.exists() and naam in idx:
        return
    print(f"    {label}", flush=True)
    try:
        d = _haal(url)
    except Exception as e:
        print(f"      OVERGESLAGEN ({e}); volgende run probeert opnieuw", flush=True)
        time.sleep(PAUZE)
        return
    pad.write_text(json.dumps(d))
    idx[naam] = meta
    _index_schrijf(idx)
    time.sleep(PAUZE)

# ── Aanroepen opbouwen ───────────────────────────────────────────────────────

def groepen():
    for i in range(0, len(STEDEN), BUNDEL):
        yield i // BUNDEL, STEDEN[i:i + BUNDEL]

def coord(groep):
    la = ",".join(str(s["lat"]) for s in groep)
    lo = ",".join(str(s["lon"]) for s in groep)
    return f"?latitude={la}&longitude={lo}"

def jaarvensters(vanaf_jaar: int):
    eind = date.fromisoformat(EIND_DATUM)
    for j in range(vanaf_jaar, eind.year + 1):
        yield j, f"{j}-01-01", (f"{j}-12-31" if j < eind.year else EIND_DATUM)

def fetch():
    print(f"Backfill {BEGIN_JAAR}-01-01 t/m {EIND_DATUM} voor {len(STEDEN)} steden\n", flush=True)

    print("1/3  ERA5 daghoogsten (waarneming-proxy)")
    for g, groep in groepen():
        sleutels = [s["key"] for s in groep]
        for j, b, e in jaarvensters(BEGIN_JAAR):
            url = ("https://archive-api.open-meteo.com/v1/archive" + coord(groep) +
                   f"&daily=temperature_2m_max&start_date={b}&end_date={e}"
                   "&temperature_unit=celsius&timezone=auto")
            gecachet(url, f"era5  groep {g + 1}  {j}",
                     {"bron": "era5", "modellen": [], "steden": sleutels})

    print("2/3  dag-0 archief (historical-forecast-api, 5 modellen per aanroep)")
    for g, groep in groepen():
        sleutels = [s["key"] for s in groep]
        for j, b, e in jaarvensters(BEGIN_JAAR):
            url = ("https://historical-forecast-api.open-meteo.com/v1/forecast" + coord(groep) +
                   f"&daily=temperature_2m_max&models={','.join(DAG0_BASIS)}"
                   f"&start_date={b}&end_date={e}&temperature_unit=celsius&timezone=auto")
            gecachet(url, f"dag0  groep {g + 1}  {j}",
                     {"bron": "dag0", "modellen": DAG0_BASIS, "steden": sleutels})

    print("2b/3 dag-0 aanvulling ecmwf_aifs025_single (vanaf 2025)")
    for g, groep in groepen():
        sleutels = [s["key"] for s in groep]
        for j, b, e in jaarvensters(2025):
            url = ("https://historical-forecast-api.open-meteo.com/v1/forecast" + coord(groep) +
                   "&daily=temperature_2m_max&models=ecmwf_aifs025_single"
                   f"&start_date={b}&end_date={e}&temperature_unit=celsius&timezone=auto")
            gecachet(url, f"dag0b groep {g + 1}  {j}",
                     {"bron": "dag0", "modellen": ["ecmwf_aifs025_single"], "steden": sleutels})

    print("3/3  previous-runs, echte lead 1 en 2 (uurdata, per modelpaar)")
    paren = [("gfs_seamless",), ("ecmwf_ifs025", "ecmwf_aifs025"),
             ("icon_seamless", "gem_seamless"), ("ecmwf_aifs025_single",)]
    for paar in paren:
        vanaf = min(PREV_START[m] for m in paar)
        for g, groep in groepen():
            sleutels = [s["key"] for s in groep]
            for j, b, e in jaarvensters(vanaf):
                url = ("https://previous-runs-api.open-meteo.com/v1/forecast" + coord(groep) +
                       "&hourly=temperature_2m_previous_day1,temperature_2m_previous_day2"
                       f"&models={','.join(paar)}&start_date={b}&end_date={e}"
                       "&temperature_unit=celsius&timezone=auto")
                gecachet(url, f"prev  {'+'.join(paar):<29} groep {g + 1}  {j}",
                         {"bron": "prev", "modellen": list(paar), "steden": sleutels})
    print("\nKlaar met ophalen.")

# ── Cache uitlezen en samenvoegen ────────────────────────────────────────────

def model_uit_sleutel(sleutel: str, modellen: list):
    for m in MODELLEN:
        if sleutel.endswith("_" + m):
            return m
    return modellen[0] if len(modellen) == 1 else None

def dagmax_uit_uren(tijden, waarden, min_uren: int = 12):
    """Max per lokale kalenderdag; minstens `min_uren` gevulde uren, anders leeg."""
    per_dag = {}
    for t, v in zip(tijden, waarden):
        if v is not None:
            per_dag.setdefault(t[:10], []).append(v)
    return {dag: max(vs) for dag, vs in per_dag.items() if len(vs) >= min_uren}

def build():
    idx  = _index_lees()
    data = {s["key"]: {} for s in STEDEN}          # key → datum → kolom → °C

    def cel(key, dag, kolom, waarde):
        data[key].setdefault(dag, {})[kolom] = round(float(waarde), 1)

    print(f"{len(idx)} cache-bestanden verwerken...", flush=True)
    for naam, meta in sorted(idx.items()):
        pad = CACHE / naam
        if not pad.exists():
            continue
        d = json.loads(pad.read_text())
        lijst = d if isinstance(d, list) else [d]
        sleutels = meta["steden"]
        if len(lijst) != len(sleutels):
            print(f"  LET OP {naam}: {len(lijst)} locaties, {len(sleutels)} verwacht")
        for key, res in zip(sleutels, lijst):
            if meta["bron"] in ("era5", "dag0") and "daily" in res:
                blok = res["daily"]; tijden = blok["time"]
                for sleutel, reeks in blok.items():
                    if sleutel == "time":
                        continue
                    if meta["bron"] == "era5":
                        kolom = "era5_max"
                    else:
                        m = model_uit_sleutel(sleutel, meta["modellen"])
                        if m is None:
                            continue
                        kolom = "d0_" + m
                    for t, v in zip(tijden, reeks):
                        if v is not None:
                            cel(key, t, kolom, v)
            elif meta["bron"] == "prev" and "hourly" in res:
                blok = res["hourly"]; tijden = blok["time"]
                for sleutel, reeks in blok.items():
                    if sleutel == "time":
                        continue
                    m = model_uit_sleutel(sleutel, meta["modellen"])
                    if m is None:
                        continue
                    lead = "p1" if "previous_day1" in sleutel else "p2"
                    for dag, mx in dagmax_uit_uren(tijden, reeks).items():
                        cel(key, dag, f"{lead}_{m}", mx)
    schrijf(data)

def schrijf(data):
    UIT.mkdir(exist_ok=True)
    kolommen = (["era5_max"] + [f"d0_{m}" for m in MODELLEN] +
                [f"p1_{m}" for m in MODELLEN] + [f"p2_{m}" for m in MODELLEN])
    kop = ["datum", "stad", "icao", "markt_eenheid"] + kolommen + ["eenheid_bestand"]

    dekking = []
    with open(UIT / "alle_steden.csv", "w", newline="") as fc:
        wc = csv.writer(fc); wc.writerow(kop)
        for s in STEDEN:
            key = s["key"]; rijen = data[key]
            f_stad = s["eenheid"] == "F"
            eenheid_markt = "°F" if f_stad else "°C"
            with open(UIT / f"{key}.csv", "w", newline="") as fs:
                ws = csv.writer(fs); ws.writerow(kop)
                for dag in sorted(rijen):
                    r = rijen[dag]
                    def w(k, naar_f):
                        v = r.get(k)
                        if v is None:
                            return ""
                        return round(v * 9 / 5 + 32, 1) if naar_f else v
                    basis = [dag, s["naam"], s["icao"], eenheid_markt]
                    ws.writerow(basis + [w(k, f_stad) for k in kolommen] + [eenheid_markt])
                    wc.writerow(basis + [w(k, False) for k in kolommen] + ["°C"])
            eerste = {k: min((dg for dg, r in rijen.items() if k in r), default="")
                      for k in kolommen}
            n_per  = {k: sum(1 for r in rijen.values() if k in r) for k in kolommen}
            dekking.append([s["naam"], s["icao"], len(rijen)] +
                           [x for k in kolommen for x in (n_per[k], eerste[k])])

    with open(UIT / "dekking.csv", "w", newline="") as fd:
        wd = csv.writer(fd)
        wd.writerow(["stad", "icao", "n_dagen"] +
                    [x for k in kolommen for x in (f"n_{k}", f"eerste_{k}")])
        wd.writerows(dekking)
    print(f"Geschreven: {len(STEDEN)} stads-CSV's + alle_steden.csv + dekking.csv → {UIT}/")


if __name__ == "__main__":
    stap = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if stap == "fetch":
        fetch()
    elif stap == "build":
        build()
    else:
        print(__doc__)
