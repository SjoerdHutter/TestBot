#!/usr/bin/env python3
"""
Deel 2 · extra voorspellers en stationswaarnemingen, 2021 t/m gisteren.

  fetch : haalt op (hervatbaar via dezelfde cache):
          a) 5 extra dagvoorspellers per stad (Open-Meteo historical, best_match):
             relatieve vochtigheid (gem), bewolking (gem), windmax, instralingssom,
             neerslagsom
          b) uurlijkse METAR-temperaturen van de 50 meetstations via IEM
          c) HKO-daghoogsten voor Hongkong
  build : voegt alles samen met de p1/p2-reeksen uit deel 1 tot een
          featurebestand per stad in uit_features/ (alles in graden Celsius)

python3 deel2_features.py fetch | build
"""
import csv, io, json, math, sys, time, urllib.request, urllib.error
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from backfill_openmeteo import (CACHE, HIER, STEDEN, EIND_DATUM, PAUZE,
                                groepen, coord, jaarvensters,
                                _index_lees, _index_schrijf)

TZ  = json.load(open(HIER / "tijdzones.json"))
UITF = HIER / "uit_features"
AUX = ["relative_humidity_2m_mean", "cloud_cover_mean", "wind_speed_10m_max",
       "shortwave_radiation_sum", "precipitation_sum"]
AUX_KORT = ["rh_gem", "bewolking_gem", "wind_max", "instraling_som", "neerslag_som"]

def iem_id(s):
    ic = s["icao"]
    return ic[1:] if ic.startswith("K") and len(ic) == 4 else ic

def _haal_tekst(url, pogingen=5, timeout=150):
    for p in range(pogingen):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "weerbot-backfill/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode(errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                print(f"      HTTP {e.code}, wachten...", flush=True)
                time.sleep(12 * (p + 1)); continue
            raise
        except Exception:
            if p == pogingen - 1:
                raise
            time.sleep(8 * (p + 1))
    raise RuntimeError("opgegeven")

def gecachet_tekst(url, label, meta):
    import hashlib
    CACHE.mkdir(exist_ok=True)
    naam = hashlib.sha1(url.encode()).hexdigest()[:20] + ".txt"
    pad  = CACHE / naam
    idx  = _index_lees()
    if pad.exists() and naam in idx:
        return
    print(f"    {label}", flush=True)
    try:
        t = _haal_tekst(url)
    except Exception as e:
        print(f"      OVERGESLAGEN ({e})", flush=True)
        time.sleep(PAUZE); return
    pad.write_text(t)
    idx[naam] = meta; _index_schrijf(idx)
    time.sleep(PAUZE)

def fetch():
    print("B  IEM METAR-uurtemperaturen (10 stations per aanroep)")
    stations = [s for s in STEDEN if s["key"] not in ("hongkong",)]
    for c in range(0, len(stations), 10):
        blok = stations[c:c + 10]
        st_q = "&".join("station=" + iem_id(s) for s in blok)
        for j, b, e in jaarvensters(2021):
            e_d = date.fromisoformat(e)
            url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?" + st_q +
                   f"&data=tmpf&year1={j}&month1=1&day1=1"
                   f"&year2={e_d.year}&month2={e_d.month}&day2={e_d.day}"
                   "&tz=Etc%2FUTC&format=comma&latlon=no&missing=M&trace=T"
                   "&direct=no&report_type=3")
            gecachet_tekst(url, f"iem   blok {c//10+1}  {j}",
                           {"bron": "iem", "stations": [iem_id(s) for s in blok]})

    print("C  HKO daghoogsten Hongkong")
    for j in range(2021, date.fromisoformat(EIND_DATUM).year + 1):
        url = ("https://data.weather.gov.hk/weatherAPI/opendata/opendata.php"
               f"?dataType=CLMMAXT&rformat=json&station=HKO&year={j}")
        gecachet_tekst(url, f"hko   {j}", {"bron": "hko", "jaar": j})
    print("A  extra dagvoorspellers (historical-forecast, best_match)")
    for g, groep in groepen():
        sleutels = [s["key"] for s in groep]
        # ERA5-archief: dezelfde vijf dagvariabelen, een bron voor alle steden.
        # Wordt na de best_match-aanroepen ingelezen en overschrijft die, zodat
        # elke stad exact dezelfde bron gebruikt (belangrijk voor het gepoolde model).
        url = ("https://archive-api.open-meteo.com/v1/archive" + coord(groep) +
               f"&daily={','.join(AUX)}&start_date=2021-01-01&end_date={EIND_DATUM}&timezone=auto")
        gecachet_tekst(url, f"aux   groep {g+1}  archief 2021 t/m nu",
                       {"bron": "aux", "steden": sleutels})

    print("Klaar met ophalen.")

# ── build ────────────────────────────────────────────────────────────────────

def f_naar_c(f): return (f - 32) * 5 / 9

def build():
    idx = _index_lees()
    # 1. basis: p1/p2 en era5 uit deel 1
    basis = {}          # key → datum → dict
    for r in csv.DictReader(open(HIER / "uit" / "alle_steden.csv")):
        naam2key = getattr(build, "_n2k", None)
        if naam2key is None:
            naam2key = {s["naam"]: s["key"] for s in STEDEN}; build._n2k = naam2key
        basis.setdefault(naam2key[r["stad"]], {})[r["datum"]] = r

    # 2. aux-voorspellers
    aux = {s["key"]: {} for s in STEDEN}
    for naam, meta in idx.items():
        if meta.get("bron") != "aux":
            continue
        lijst = json.loads((CACHE / naam).read_text())
        lijst = lijst if isinstance(lijst, list) else [lijst]
        for key, res in zip(meta["steden"], lijst):
            d = res.get("daily", {})
            for i, t in enumerate(d.get("time", [])):
                rij = {}
                for lang, kort in zip(AUX, AUX_KORT):
                    v = d.get(lang, [None]*len(d["time"]))[i]
                    if v is not None:
                        rij[kort] = v
                if rij:
                    aux[key].setdefault(t, {}).update(rij)

    # 3. IEM-stationswaarnemingen → daghoogste per lokale kalenderdag
    per_station = {}    # iem-id → list[(utc_dt, tmpf)]
    for naam, meta in idx.items():
        if meta.get("bron") != "iem":
            continue
        for regel in (CACHE / naam).read_text().splitlines():
            if regel.startswith("#") or regel.startswith("station,"):
                continue
            d = regel.split(",")
            if len(d) < 3 or d[2] in ("M", ""):
                continue
            try:
                per_station.setdefault(d[0], []).append(
                    (datetime.strptime(d[1], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc),
                     float(d[2])))
            except ValueError:
                continue

    station_max = {s["key"]: {} for s in STEDEN}
    for s in STEDEN:
        if s["key"] == "hongkong":
            continue
        tz = ZoneInfo(TZ[s["key"]])
        per_dag = {}
        for dt_utc, tf in per_station.get(iem_id(s), []):
            lok = dt_utc.astimezone(tz)
            per_dag.setdefault(lok.date().isoformat(), []).append((lok.hour, tf))
        for dag, obs in per_dag.items():
            # geldigheidseis: minstens 8 waarnemingen en minstens één tussen 10 en 18 u
            if len(obs) >= 8 and any(10 <= u <= 18 for u, _ in obs):
                station_max[s["key"]][dag] = round(f_naar_c(max(t for _, t in obs)), 1)

    # 4. HKO
    for naam, meta in idx.items():
        if meta.get("bron") != "hko":
            continue
        d = json.loads((CACHE / naam).read_text())
        for rij in d.get("data", []):
            try:
                j, m, dg, v = int(rij[0]), int(rij[1]), int(rij[2]), float(rij[3])
                station_max["hongkong"][f"{j:04d}-{m:02d}-{dg:02d}"] = v
            except (ValueError, IndexError):
                continue

    # 5. samenvoegen en wegschrijven
    UITF.mkdir(exist_ok=True)
    P1 = ["p1_ecmwf_ifs025", "p1_ecmwf_aifs025", "p1_ecmwf_aifs025_single",
          "p1_gfs_seamless", "p1_icon_seamless", "p1_gem_seamless"]
    P2 = [k.replace("p1_", "p2_") for k in P1]
    kop = (["datum", "p1_ifs", "p1_aifs", "p1_gfs", "p1_icon", "p1_gem",
            "p2_ifs", "p2_aifs", "p2_gfs", "p2_icon", "p2_gem",
            "mm_gem", "mm_spreiding", "run2run"] + AUX_KORT +
           ["doy_sin", "doy_cos", "era5_max", "station_max", "doel", "doelbron"])

    telling = []
    for s in STEDEN:
        key = s["key"]
        with open(UITF / f"{key}.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(kop)
            n_doel = 0
            for dag in sorted(basis.get(key, {})):
                b = basis[key][dag]
                def g(k):
                    v = b.get(k, "")
                    return float(v) if v else None
                p1 = {"ifs": g(P1[0]),
                      "aifs": g(P1[2]) if g(P1[2]) is not None else g(P1[1]),
                      "gfs": g(P1[3]), "icon": g(P1[4]), "gem": g(P1[5])}
                p2 = {"ifs": g(P2[0]),
                      "aifs": g(P2[2]) if g(P2[2]) is not None else g(P2[1]),
                      "gfs": g(P2[3]), "icon": g(P2[4]), "gem": g(P2[5])}
                p1v = [v for v in p1.values() if v is not None]
                p2v = [v for v in p2.values() if v is not None]
                mm = sp = r2r = None
                if len(p1v) >= 4:
                    mm = sum(p1v) / len(p1v)
                    sp = (sum((x - mm) ** 2 for x in p1v) / (len(p1v) - 1)) ** 0.5
                    if len(p2v) >= 4:
                        r2r = mm - sum(p2v) / len(p2v)
                a = aux[key].get(dag, {})
                dt = date.fromisoformat(dag)
                doy = dt.timetuple().tm_yday / 365.25 * 2 * math.pi
                stm = station_max[key].get(dag)
                if key == "jinan":
                    doel, bron = g("era5_max"), "era5"
                else:
                    doel, bron = stm, ("station" if stm is not None else "")
                if doel is not None:
                    n_doel += 1
                rond = lambda v, d=1: ("" if v is None else round(v, d))
                w.writerow([dag] +
                           [rond(p1[k]) for k in ("ifs","aifs","gfs","icon","gem")] +
                           [rond(p2[k]) for k in ("ifs","aifs","gfs","icon","gem")] +
                           [rond(mm, 2), rond(sp, 2), rond(r2r, 2)] +
                           [a.get(k, "") for k in AUX_KORT] +
                           [round(math.sin(doy), 4), round(math.cos(doy), 4),
                            b.get("era5_max", ""), rond(stm), rond(doel), bron])
        telling.append((key, n_doel))
    dun = [t for t in telling if t[1] < 1500]
    print(f"{len(telling)} featurebestanden → {UITF}/")
    print("steden met < 1500 doeldagen:", dun if dun else "geen")

if __name__ == "__main__":
    (fetch if (sys.argv[1:] or ["fetch"])[0] == "fetch" else build)()
