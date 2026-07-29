#!/usr/bin/env python3
"""
Deel 8 · perfect-prognosis microklimaatmodel, getraind op 2000 t/m 2020.

  stagea  : per stad delta = station − ERA5 leren uit ~21 jaar (lineair + GBM),
            houdbaarheidstoets op 2019 t/m 2020, daarna klim-features berekenen
            voor 2021+ (gridtemperatuur = mm_gem op voorspelmoment)
  wf      : walk-forward voor de kandidaat ridge+klim (lineaire en GBM-variant)
  rapport : vergelijking met de zittende kampioen; upgrades (binnen de
            ridge-familie: ΔMAE ≥ 0,02 °C én p < 0,05) en labelwissels
            (volledige ML-regel én standhouden in beide helften); export

Serveerlogica: stage A is getraind met ERA5-invoer en wordt toegepast op de
voorspelde gridtoestand (mm_gem) plus de voorspelde weersvariabelen; klassieke
perfect prognosis.
"""
import csv, json, math, pickle, sys
from datetime import date
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor

from deel3_train import laad_stad, matrix, P1, AUX, MAANDEN, STEDEN, HIER

FEATS  = P1 + ["mm_spreiding", "run2run", "doy_sin", "doy_cos", "lag2_err"] + AUX
LANG   = HIER / "lang"
MODDIR = HIER / "modellen"
KLIMF  = HIER / "klim_features.csv"
VKLIM  = HIER / "voorspellingen_klim.csv"
KLAARK = HIER / "klaar_klim.json"
SA_IN  = ["era5_max"] + AUX + ["doy_sin", "doy_cos"]   # serveren: mm_gem i.p.v. era5_max
MIN_DAGEN = 1000

def _lang(key):
    rijen = list(csv.DictReader(open(LANG / f"{key}.csv")))
    kol = {}
    for k in ["era5_max", "station_max"] + AUX:
        kol[k] = np.array([float(r[k]) if r[k] else np.nan for r in rijen])
    dagen = [r["datum"] for r in rijen]
    doy = np.array([date.fromisoformat(d).timetuple().tm_yday for d in dagen]) / 365.25 * 2 * math.pi
    kol["doy_sin"], kol["doy_cos"] = np.sin(doy), np.cos(doy)
    return np.array(dagen), kol

def stagea():
    MODDIR.mkdir(exist_ok=True)
    exp_lin, overzicht = {}, []
    modellen_g = {}
    for s in STEDEN:
        key = s["key"]
        if key == "jinan":
            continue
        dagen, kol = _lang(key)
        ok = np.isfinite(kol["era5_max"]) & np.isfinite(kol["station_max"])
        for a in AUX:
            ok &= np.isfinite(kol[a])
        delta = kol["station_max"] - kol["era5_max"]
        ok &= np.abs(delta) < 15
        idx = np.where(ok)[0]
        if len(idx) < MIN_DAGEN:
            continue
        X = np.column_stack([kol[k][idx] for k in SA_IN]); y = delta[idx]
        da = dagen[idx]
        tr = da < "2019-01-01"; te = ~tr
        if tr.sum() < 500 or te.sum() < 200:
            continue
        mu, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1
        ri = Ridge(alpha=1.0).fit((X[tr] - mu) / sd, y[tr])
        gb = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06,
             max_leaf_nodes=31, min_samples_leaf=50, l2_regularization=1.0,
             random_state=1).fit(X[tr], y[tr])
        mnd = np.array([int(d[5:7]) for d in da])
        klim_m = {m: (y[tr & (mnd == m)].mean() if (tr & (mnd == m)).any() else 0.0)
                  for m in range(1, 13)}
        basis_m = np.array([klim_m[m] for m in mnd[te]])
        overzicht.append([np.mean(np.abs(y[te])),
                          np.mean(np.abs(y[te] - basis_m)),
                          np.mean(np.abs(y[te] - ri.predict((X[te] - mu) / sd))),
                          np.mean(np.abs(y[te] - gb.predict(X[te])))])
        # eindfit op alle jaren
        mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1
        ri = Ridge(alpha=1.0).fit((X - mu) / sd, y)
        gb = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06,
             max_leaf_nodes=31, min_samples_leaf=50, l2_regularization=1.0,
             random_state=1).fit(X, y)
        exp_lin[key] = {"inputs": SA_IN, "mu": mu.round(4).tolist(),
                        "sd": sd.round(4).tolist(),
                        "coef": ri.coef_.round(5).tolist(),
                        "intercept": round(float(ri.intercept_), 4),
                        "n_train": int(len(y))}
        modellen_g[key] = gb
        pickle.dump({"model": gb, "inputs": SA_IN},
                    open(MODDIR / f"stagea_gbm_{key}.pkl", "wb"))
    json.dump(exp_lin, open(MODDIR / "stagea_lineair.json", "w"))
    o = np.array(overzicht)
    print(f"stage A · {len(exp_lin)} steden getraind (2000 t/m 2020)")
    print(("houdbaarheid 2019 t/m 2020, MAE van delta (°C): nulmodel "
           f"{o[:,0].mean():.3f} · maandklimatologie {o[:,1].mean():.3f} · "
           f"lineair {o[:,2].mean():.3f} · gbm {o[:,3].mean():.3f}").replace(".", ","))

    # klim-features 2021+ (gridtemperatuur = mm_gem)
    with open(KLIMF, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["key", "datum", "klimL", "klimG"])
        for s in STEDEN:
            key = s["key"]
            dagen, kol = laad_stad(key)
            inp = ["mm_gem"] + AUX + ["doy_sin", "doy_cos"]
            M = np.column_stack([kol[k] for k in inp])
            geldig = np.all(np.isfinite(M), axis=1)
            if key in exp_lin:
                e = exp_lin[key]
                mu = np.array(e["mu"]); sd = np.array(e["sd"])
                kl = ((M - mu) / sd) @ np.array(e["coef"]) + e["intercept"]
                kg = np.full(len(M), np.nan)
                kg[geldig] = modellen_g[key].predict(M[geldig])
            else:
                kl = np.zeros(len(M)); kg = np.zeros(len(M)); geldig = np.ones(len(M), bool)
            for i in np.where(geldig)[0]:
                w.writerow([key, dagen[i], round(float(kl[i]), 3), round(float(kg[i]), 3)])
    print(f"klim-features → {KLIMF.name}")

def _klim():
    kl = {}
    for r in csv.DictReader(open(KLIMF)):
        kl[(r["key"], r["datum"])] = (float(r["klimL"]), float(r["klimG"]))
    return kl

def wf():
    kl = _klim()
    data = {s["key"]: laad_stad(s["key"]) for s in STEDEN}
    naam = {s["key"]: s["naam"] for s in STEDEN}
    klaar = json.load(open(KLAARK)) if KLAARK.exists() else []
    nieuw = not VKLIM.exists()
    fu = open(VKLIM, "a", newline=""); w = csv.writer(fu)
    if nieuw:
        w.writerow(["maand", "stad", "datum", "doel", "klimL", "klimG"])
    for maand in MAANDEN:
        if maand in klaar:
            continue
        grens = maand + "-01"; n_rij = 0
        for key, (datums, kol) in data.items():
            da = np.array(datums)
            geldig = np.isfinite(kol["mm_gem"]) & np.isfinite(kol["doel"])
            tr = np.where(geldig & (da < grens))[0]
            te = np.where(geldig & np.char.startswith(da, maand))[0]
            if len(tr) < 60 or not len(te):
                continue
            X_tr, med = matrix(kol, tr, FEATS)
            X_te, _   = matrix(kol, te, FEATS, med)
            uit = {}
            for var, ix in (("klimL", 0), ("klimG", 1)):
                c_tr = np.array([kl.get((key, datums[i]), (0.0, 0.0))[ix] for i in tr])
                c_te = np.array([kl.get((key, datums[i]), (0.0, 0.0))[ix] for i in te])
                A_tr = np.column_stack([X_tr, c_tr]); A_te = np.column_stack([X_te, c_te])
                mu, sd = A_tr.mean(0), A_tr.std(0); sd[sd == 0] = 1
                ri = Ridge(alpha=1.0).fit((A_tr - mu) / sd, kol["doel"][tr])
                uit[var] = ri.predict((A_te - mu) / sd)
            for j, i in enumerate(te):
                w.writerow([maand, naam[key], datums[i], round(float(kol["doel"][i]), 2),
                            round(float(uit["klimL"][j]), 2), round(float(uit["klimG"][j]), 2)])
                n_rij += 1
        fu.flush(); klaar.append(maand); json.dump(klaar, open(KLAARK, "w"))
        print(f"  {maand}: {n_rij} klim-testdagen", flush=True)
    fu.close(); print("wf klaar")

def rapport():
    basis = {(r["stad"], r["datum"]): r for r in csv.DictReader(open(HIER / "voorspellingen.csv"))}
    res   = {r["stad"]: r for r in csv.DictReader(open(HIER / "resultaten.csv"))}
    vk    = list(csv.DictReader(open(VKLIM)))
    N = len(res)

    def toets(p, marge_eis, rel_eis):
        pr = np.array(p)
        if len(pr) < 60:
            return False, np.nan, np.nan, np.nan
        a, b = pr[:, 0], pr[:, 1]
        d = a - b
        t = d.mean() / (d.std(ddof=1) / math.sqrt(len(d)) + 1e-12)
        pw = math.erfc(abs(t) / math.sqrt(2))
        m = a.mean() - b.mean()
        return (m >= marge_eis and m >= rel_eis * a.mean() and pw < 0.05), pw, a.mean(), b.mean()

    per = {}
    for r in vk:
        per.setdefault(r["stad"], []).append(r)

    rijen_uit, upgrades, flips = [], [], []
    for s in STEDEN:
        naam = s["naam"]; rr = res[naam]
        kamp = "ref_lin" if rr["label"] == "LINEAIR" else rr["gekozen_variant"]
        pk, pr_r = {"klimL": [], "klimG": []}, {"klimL": [], "klimG": []}
        halves = {"klimL": [[], []], "klimG": [[], []]}
        for r in per.get(naam, []):
            b = basis.get((naam, r["datum"]))
            if not (b and b["doel"]):
                continue
            doel = float(b["doel"])
            for var in ("klimL", "klimG"):
                if not r[var]:
                    continue
                fk = abs(float(r[var]) - doel)
                if b.get(kamp):
                    paar = (abs(float(b[kamp]) - doel), fk)
                    pk[var].append(paar)
                    halves[var][0 if r["datum"] < "2025-10-01" else 1].append(paar)
                if b.get("ridge"):
                    pr_r[var].append((abs(float(b["ridge"]) - doel), fk))
        beste = min(("klimL", "klimG"),
                    key=lambda v: np.mean([x[1] for x in pk[v]]) if pk[v] else 9e9)
        ok_up, p_up, m_ri, m_kl = toets(pr_r[beste], 0.02, 0.0)
        ok_fl, p_fl, m_kamp, _ = toets(pk[beste], 0.03, 0.02)
        ok_h1, *_ = toets(halves[beste][0], 0.03, 0.02)
        ok_h2, *_ = toets(halves[beste][1], 0.03, 0.02)
        if rr["label"] == "ML" and ok_up:
            upgrades.append((naam, beste, round(m_ri, 3), round(m_kl, 3), round(p_up, 4)))
        if rr["label"] in ("LINEAIR", "GEPOOLD") and ok_fl and ok_h1 and ok_h2 and p_fl * N < 0.05:
            flips.append((naam, beste, round(m_kamp, 3), round(m_kl, 3), round(p_fl, 5)))
        rd = lambda v: ("" if not np.isfinite(v) else round(v, 3))
        rijen_uit.append([naam, rr["label"], kamp, beste, rd(m_kamp), rd(m_ri), rd(m_kl),
                          rd(p_up), int(ok_up), int(ok_fl and ok_h1 and ok_h2)])

    with open(HIER / "resultaten_klim.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stad", "label_nu", "kampioen", "beste_klimvariant", "mae_kampioen",
                    "mae_ridge", "mae_ridge_klim", "p_vs_ridge", "upgrade", "flip"])
        w.writerows(rijen_uit)
    g = lambda i: float(np.mean([x[i] for x in rijen_uit if x[i] != ""]))
    print(f"gemiddelde MAE: kampioen {g(4):.3f} · ridge {g(5):.3f} · ridge+klim {g(6):.3f}".replace(".", ","))
    print(f"upgrades binnen ridge-familie ({len(upgrades)}):", upgrades if upgrades else "geen")
    print(f"labelwissels naar ML ({len(flips)}):", flips if flips else "geen")
    print("resultaten_klim.csv geschreven")

if __name__ == "__main__":
    stap = (sys.argv[1:] or ["stagea"])[0]
    {"stagea": stagea, "wf": wf, "rapport": rapport}[stap]()
