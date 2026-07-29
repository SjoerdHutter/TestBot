#!/usr/bin/env python3
"""
Deel 7 · lange backfill 2000 t/m 2020 voor het perfect-prognosis deelmodel.

  fetch : a) ERA5 daghoogste + de vijf weersvariabelen per stad (archief)
          b) IEM METAR-uurtemperaturen 2000 t/m 2020 (10 stations × 3 jaar per
             aanroep), c) HKO-daghoogsten 2000 t/m 2020
  build : streaming samenvoegen naar lang/<stad>.csv met per datum:
          era5_max, de vijf weersvariabelen en station_max

Hervatbaar via dezelfde cache. Kanttekeningen: stations die pas later
bestonden (LTFM 2018, ZSQD = Liuting vóór 2021) leveren minder of gemengde
historie; dat is een eigenschap van de werkelijkheid, niet van de code.
"""
import csv, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from backfill_openmeteo import CACHE, HIER, STEDEN, PAUZE, groepen, coord, _index_lees
from deel2_features import gecachet_tekst, iem_id, AUX, AUX_KORT, f_naar_c

TZ   = json.load(open(HIER / "tijdzones.json"))
LANG = HIER / "lang"
IEM_VENSTERS = [(j, min(j + 2, 2020)) for j in range(2000, 2021, 3)]

def fetch():
    print("B  HKO daghoogsten 2000 t/m 2020")
    for j in range(2000, 2021):
        url = ("https://data.weather.gov.hk/weatherAPI/opendata/opendata.php"
               f"?dataType=CLMMAXT&rformat=json&station=HKO&year={j}")
        gecachet_tekst(url, f"hkoL  {j}", {"bron": "hkoL", "jaar": j})

    print("C  IEM METAR-uurtemperaturen 2000 t/m 2020 (35 aanroepen)")
    stations = [s for s in STEDEN if s["key"] != "hongkong"]
    for c in range(0, len(stations), 10):
        blok = stations[c:c + 10]
        st_q = "&".join("station=" + iem_id(s) for s in blok)
        for j1, j2 in IEM_VENSTERS:
            url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?" + st_q +
                   f"&data=tmpf&year1={j1}&month1=1&day1=1&year2={j2}&month2=12&day2=31"
                   "&tz=Etc%2FUTC&format=comma&latlon=no&missing=M&trace=T"
                   "&direct=no&report_type=3")
            gecachet_tekst(url, f"iemL  blok {c//10+1}  {j1} tot {j2}",
                           {"bron": "iemL", "stations": [iem_id(s) for s in blok]})
    print("A  ERA5 lang: daghoogste + vijf weersvariabelen, 2000 t/m 2020")
    for g, groep in groepen():
        sleutels = [s["key"] for s in groep]
        for b, e in [("2000-01-01", "2010-12-31"), ("2011-01-01", "2020-12-31")]:
            url = ("https://archive-api.open-meteo.com/v1/archive" + coord(groep) +
                   f"&daily=temperature_2m_max,{','.join(AUX)}"
                   f"&start_date={b}&end_date={e}&timezone=auto")
            gecachet_tekst(url, f"era5L groep {g+1}  {b[:4]} tot {e[:4]}",
                           {"bron": "era5L", "steden": sleutels})

    print("Klaar met ophalen.")

# ── build (streaming, geheugenzuinig) ────────────────────────────────────────

def build():
    idx = _index_lees()
    key_per_iem = {iem_id(s): s["key"] for s in STEDEN if s["key"] != "hongkong"}
    tzcache = {k: ZoneInfo(TZ[k]) for k in key_per_iem.values()}

    # station → datum → [n_obs, max_f, middag_gezien]
    agg = {}
    era = {s["key"]: {} for s in STEDEN}   # key → datum → dict
    for naam, meta in sorted(idx.items()):
        pad = CACHE / naam
        if not pad.exists():
            continue
        bron = meta.get("bron")
        if bron == "iemL":
            with open(pad) as f:
                for regel in f:
                    if regel.startswith(("#", "station,")):
                        continue
                    d = regel.rstrip("\n").split(",")
                    if len(d) < 3 or d[2] in ("M", ""):
                        continue
                    key = key_per_iem.get(d[0])
                    if not key:
                        continue
                    try:
                        v = d[1]  # 'YYYY-MM-DD HH:MM' in UTC
                        dt = datetime(int(v[0:4]), int(v[5:7]), int(v[8:10]),
                                      int(v[11:13]), int(v[14:16]),
                                      tzinfo=timezone.utc).astimezone(tzcache[key])
                        tf = float(d[2])
                    except (ValueError, IndexError):
                        continue
                    e = agg.setdefault(key, {}).setdefault(dt.date().isoformat(),
                                                           [0, -999.0, False])
                    e[0] += 1
                    if tf > e[1]:
                        e[1] = tf
                    if 10 <= dt.hour <= 18:
                        e[2] = True
        elif bron == "era5L":
            lijst = json.loads(pad.read_text())
            lijst = lijst if isinstance(lijst, list) else [lijst]
            for key, res in zip(meta["steden"], lijst):
                dd = res.get("daily", {})
                tijden = dd.get("time", [])
                for i, t in enumerate(tijden):
                    rij = era[key].setdefault(t, {})
                    v = dd.get("temperature_2m_max", [None]*len(tijden))[i]
                    if v is not None:
                        rij["era5_max"] = v
                    for lang_n, kort in zip(AUX, AUX_KORT):
                        v = dd.get(lang_n, [None]*len(tijden))[i]
                        if v is not None:
                            rij[kort] = v
        elif bron == "hkoL":
            d = json.loads(pad.read_text())
            for rij in d.get("data", []):
                try:
                    j, m, dg, v = int(rij[0]), int(rij[1]), int(rij[2]), float(rij[3])
                    agg.setdefault("hongkong", {})[f"{j:04d}-{m:02d}-{dg:02d}"] = [99, v, True]
                except (ValueError, IndexError):
                    continue

    LANG.mkdir(exist_ok=True)
    telling = []
    for s in STEDEN:
        key = s["key"]
        with open(LANG / f"{key}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["datum", "era5_max"] + AUX_KORT + ["station_max"])
            n_st = 0
            for dag in sorted(era[key]):
                r = era[key][dag]
                st = ""
                e = agg.get(key, {}).get(dag)
                if e and e[0] >= 8 and e[2]:
                    st = round(e[1] if key == "hongkong" else f_naar_c(e[1]), 1)
                    n_st += 1
                w.writerow([dag, r.get("era5_max", "")] +
                           [r.get(k, "") for k in AUX_KORT] + [st])
        telling.append((key, n_st))
    dun = sorted([t for t in telling if t[1] < 5000], key=lambda x: x[1])
    print(f"{len(telling)} lange bestanden → {LANG}/")
    print("steden met < 5000 stationsdagen (2000 t/m 2020):", dun if dun else "geen")

if __name__ == "__main__":
    (fetch if (sys.argv[1:] or ["fetch"])[0] == "fetch" else build)()
