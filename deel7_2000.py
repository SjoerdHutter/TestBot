#!/usr/bin/env python3
"""
Deel 5 · toelatingstoets voor een nieuwe modelfamilie (zoals het NN van deel 4).

Per stad wordt de kandidaat vergeleken met de ZITTENDE kampioen (de gekozen
variant uit resultaten.csv), niet met de zwakste baseline. Toelating per stad
alleen als alle drie gelden:
  1. winst volgens de ML-regel (>= 0,03 °C en >= 2% en p < 0,05) in BEIDE
     helften van de walk-forward,
  2. Bonferroni over alle steden: p x n_steden < 0,05,
  3. daarna standhouden op de live-log gedurende 60 dagen (handmatige stap).
Familietoelating (kandidaat wordt vaste kandidaat in deel 3) zodra hij in
>= 5 steden tegelijk wint: ruim boven de ruisvloer van ~2 a 3 valse winnaars
die je bij 51 toetsen op p < 0,05 sowieso verwacht.

Gebruik: python3 deel5_robuustheid.py  (leest voorspellingen*.csv)
"""
import csv, math
import numpy as np

basis = {(r["stad"], r["datum"]): r for r in csv.DictReader(open("voorspellingen.csv"))}
nn    = {(r["stad"], r["datum"]): r for r in csv.DictReader(open("voorspellingen_nn.csv"))}
res   = {r["stad"]: r for r in csv.DictReader(open("resultaten.csv"))}
N     = len(res)

def paren(stad, kamp, van="0000", tot="9999"):
    uit = []
    for (s, d), r in basis.items():
        q = nn.get((s, d))
        if s != stad or not (van <= d < tot) or not (r["doel"] and r.get(kamp) and q and q["nn"]):
            continue
        doel = float(r["doel"])
        uit.append((abs(float(r[kamp]) - doel), abs(float(q["nn"]) - doel)))
    return uit

def toets(p):
    if len(p) < 60:
        return False, np.nan, np.nan, np.nan
    a = np.array([x[0] for x in p]); b = np.array([x[1] for x in p])
    d = a - b
    t = d.mean() / (d.std(ddof=1) / math.sqrt(len(d)) + 1e-12)
    pw = math.erfc(abs(t) / math.sqrt(2))
    m = a.mean() - b.mean()
    return (m >= 0.03 and m >= 0.02 * a.mean() and pw < 0.05), pw, a.mean(), b.mean()

toegelaten = []
for stad, r in res.items():
    kamp = "ref_lin" if r["label"] == "LINEAIR" else r["gekozen_variant"]
    ok,  p,  mk, mn = toets(paren(stad, kamp))
    ok1, *_ = toets(paren(stad, kamp, "2025-01", "2025-10"))
    ok2, *_ = toets(paren(stad, kamp, "2025-10", "2026-08"))
    if ok and ok1 and ok2 and p * N < 0.05:
        toegelaten.append((stad, kamp, round(mk, 3), round(mn, 3), round(p, 5)))

print(f"kandidaat NN · steden die de volledige toelatingstoets halen: "
      f"{toegelaten if toegelaten else 'geen'}")
print(f"familietoelating (>= 5 steden): {'JA' if len(toegelaten) >= 5 else 'NEE'}")
