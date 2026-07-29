#!/usr/bin/env python3
"""
Deel 3 · per stad trainen en backtesten tegen de stationswaarnemingen.

  train   : walk-forward (maandelijks bijtrainen), testmaanden 2025-01 t/m 2026-07,
            hervatbaar per maand (klaar.json + voorspellingen.csv)
  rapport : metriek per stad, ML-beslisregel, NGR-spreidingsfit, eindmodellen
            hertrainen op alle data en exporteren naar modellen/

Varianten (alles in °C):
  ruw      multi-model-gemiddelde zonder correctie
  ref_lin  huidige stijl: a + b·mm + g·lagfout (per stad, OLS)
  ridge    lineair met alle voorspellers (per stad, gestandaardiseerd, alpha 1,0)
  gbm      HistGradientBoosting per stad
  pooled   HistGradientBoosting over alle steden samen (+ lat/lon + stad-categorie)

Beslisregel per stad:
  backtestbaar  = n_test ≥ 120 én n_train(eind) ≥ 250
  ML            = beste van (ridge, gbm) verslaat ref_lin met ≥ 0,03 °C én ≥ 2%
                  én gepaarde toets p < 0,05
  anders GEPOOLD als pooled ref_lin met dezelfde marge verslaat, anders LINEAIR
  niet-backtestbaar → GEPOOLD (vraag 2.2)
"""
import csv, json, math, pickle, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor

HIER   = Path(__file__).parent
UITF   = HIER / "uit_features"
STEDEN = json.load(open(HIER / "steden.json"))
MODDIR = HIER / "modellen"
VOORSP = HIER / "voorspellingen.csv"
KLAAR  = HIER / "klaar.json"

AUX = ["rh_gem", "bewolking_gem", "wind_max", "instraling_som", "neerslag_som"]
P1  = ["p1_ifs", "p1_aifs", "p1_gfs", "p1_icon", "p1_gem"]
MAANDEN = [f"{j}-{m:02d}" for j in (2025, 2026) for m in range(1, 13)][:19]

# ── laden ────────────────────────────────────────────────────────────────────

def laad_stad(key):
    rijen = list(csv.DictReader(open(UITF / f"{key}.csv")))
    n = len(rijen)
    kol = {}
    for k in ["mm_gem", "mm_spreiding", "run2run", "doy_sin", "doy_cos", "doel"] + P1 + AUX:
        kol[k] = np.array([float(r[k]) if r[k] else np.nan for r in rijen])
    datums = [r["datum"] for r in rijen]
    lag = np.zeros(n)
    fout = kol["doel"] - kol["mm_gem"]
    for i in range(n):
        for d in (2, 3):
            if i - d >= 0 and np.isfinite(fout[i - d]):
                lag[i] = fout[i - d]; break
    kol["lag2_err"] = lag
    return datums, kol

def matrix(kol, idx, feats, med=None):
    X = []
    for k in feats:
        v = kol[k][idx].copy()
        if k in P1:
            v = np.where(np.isfinite(v), v, kol["mm_gem"][idx])
        if k == "run2run":
            v = np.where(np.isfinite(v), v, 0.0)
        X.append(v)
    X = np.column_stack(X)
    if med is None:
        med = np.nanmedian(X, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
    X = np.where(np.isfinite(X), X, med)
    return X, med

def ols(X, y):
    A = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    return b

# ── train (walk-forward, hervatbaar) ─────────────────────────────────────────

def train():
    data = {s["key"]: laad_stad(s["key"]) for s in STEDEN}
    # aux meenemen als hij in het multi-modeltijdperk voldoende gevuld is
    vul = []
    for key, (datums, kol) in data.items():
        m = np.array([d >= "2024-04-01" for d in datums])
        vul.append(np.mean([np.mean(np.isfinite(kol[a][m])) for a in AUX]))
    aux_actief = float(np.mean(vul)) >= 0.30
    feats = P1 + ["mm_spreiding", "run2run", "doy_sin", "doy_cos", "lag2_err"] + (AUX if aux_actief else [])
    print(f"features ({len(feats)}): aux {'meegenomen' if aux_actief else 'weggelaten (te leeg)'}")

    klaar = json.load(open(KLAAR)) if KLAAR.exists() else []
    nieuw = not VOORSP.exists()
    fu = open(VOORSP, "a", newline="")
    w = csv.writer(fu)
    if nieuw:
        w.writerow(["maand", "stad", "datum", "doel", "ruw", "ref_lin", "ridge", "gbm", "pooled"])

    extra = {s["key"]: (s["lat"], abs(s["lat"]), s["lon"], i) for i, s in enumerate(STEDEN)}
    for maand in MAANDEN:
        if maand in klaar:
            continue
        grens = maand + "-01"
        # gepoold trainen
        Xp, yp = [], []
        per_stad = {}
        for key, (datums, kol) in data.items():
            da = np.array(datums)
            geldig = np.isfinite(kol["mm_gem"]) & np.isfinite(kol["doel"])
            tr = np.where(geldig & (da < grens))[0]
            te = np.where(geldig & np.char.startswith(da, maand))[0]
            per_stad[key] = (tr, te)
            if len(tr):
                X, med = matrix(kol, tr, feats)
                Xp.append(np.column_stack([X] + [np.full(len(tr), v) for v in extra[key]]))
                yp.append(kol["doel"][tr])
        pooled = None
        if Xp:
            Xp = np.vstack(Xp); yp = np.concatenate(yp)
            if len(yp) >= 2000:
                pooled = HistGradientBoostingRegressor(
                    max_iter=150, learning_rate=0.07, max_leaf_nodes=31,
                    min_samples_leaf=40, l2_regularization=1.0,
                    categorical_features=[Xp.shape[1] - 1], random_state=1)
                pooled.fit(Xp, yp)

        n_rij = 0
        for key, (datums, kol) in data.items():
            tr, te = per_stad[key]
            if not len(te):
                continue
            y_tr, y_te = kol["doel"][tr], kol["doel"][te]
            mm_te = kol["mm_gem"][te]
            uit = {"ruw": mm_te,
                   "ref_lin": np.full(len(te), np.nan),
                   "ridge":   np.full(len(te), np.nan),
                   "gbm":     np.full(len(te), np.nan),
                   "pooled":  np.full(len(te), np.nan)}
            if len(tr) >= 60:
                Xl_tr = np.column_stack([kol["mm_gem"][tr], kol["lag2_err"][tr]])
                co = ols(Xl_tr, y_tr)
                uit["ref_lin"] = co[0] + co[1] * mm_te + co[2] * kol["lag2_err"][te]
                X_tr, med = matrix(kol, tr, feats)
                X_te, _   = matrix(kol, te, feats, med)
                mu, sd = X_tr.mean(0), X_tr.std(0); sd[sd == 0] = 1
                ri = Ridge(alpha=1.0).fit((X_tr - mu) / sd, y_tr)
                uit["ridge"] = ri.predict((X_te - mu) / sd)
                if len(tr) >= 100:
                    gb = HistGradientBoostingRegressor(
                        max_iter=120, learning_rate=0.07, max_leaf_nodes=15,
                        min_samples_leaf=20, l2_regularization=1.0, random_state=1)
                    gb.fit(X_tr, y_tr)
                    uit["gbm"] = gb.predict(X_te)
                if pooled is not None:
                    Xe = np.column_stack([X_te] + [np.full(len(te), v) for v in extra[key]])
                    uit["pooled"] = pooled.predict(Xe)
            naam = {s["key"]: s["naam"] for s in STEDEN}[key]
            for i, ix in enumerate(te):
                rond = lambda v: "" if not np.isfinite(v) else round(float(v), 2)
                w.writerow([maand, naam, datums[ix], rond(y_te[i]), rond(uit["ruw"][i]),
                            rond(uit["ref_lin"][i]), rond(uit["ridge"][i]),
                            rond(uit["gbm"][i]), rond(uit["pooled"][i])])
                n_rij += 1
        fu.flush()
        klaar.append(maand)
        json.dump(klaar, open(KLAAR, "w"))
        print(f"  {maand}: {n_rij} testdagen weggeschreven", flush=True)
    fu.close()
    print("train klaar:", len(klaar), "maanden")

# ── rapport en export ────────────────────────────────────────────────────────

from scipy.special import erf as _erf

def crps_gauss(e, s):
    z = e / s
    Phi = 0.5 * (1 + _erf(z / math.sqrt(2)))
    phi = np.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    return np.mean(s * (z * (2 * Phi - 1) + 2 * phi - 1 / math.sqrt(math.pi)))

def rapport():
    rijen = list(csv.DictReader(open(VOORSP)))
    per = {}
    for r in rijen:
        per.setdefault(r["stad"], []).append(r)
    data = {s["key"]: laad_stad(s["key"]) for s in STEDEN}
    naam2 = {s["naam"]: s for s in STEDEN}
    MODDIR.mkdir(exist_ok=True)

    feats = P1 + ["mm_spreiding", "run2run", "doy_sin", "doy_cos", "lag2_err"]
    res, ml_export, lab_telling = [], {}, {}
    for s in STEDEN:
        naam, key = s["naam"], s["key"]
        rs = [r for r in per.get(naam, []) if r["doel"]]
        def fouten(k):
            return np.array([abs(float(r[k]) - float(r["doel"])) for r in rs if r[k]])
        def paren(k):
            return np.array([(abs(float(r["ref_lin"]) - float(r["doel"])),
                              abs(float(r[k]) - float(r["doel"])))
                             for r in rs if r[k] and r["ref_lin"]])
        n_test = len([r for r in rs if r["ref_lin"]])
        datums, kol = data[key]
        geldig = np.isfinite(kol["mm_gem"]) & np.isfinite(kol["doel"])
        n_train = int(np.sum(geldig & (np.array(datums) < "2026-07-01")))
        mae = {k: (float(np.mean(fouten(k))) if len(fouten(k)) else np.nan)
               for k in ("ruw", "ref_lin", "ridge", "gbm", "pooled")}
        backtestbaar = n_test >= 120 and n_train >= 250

        label, variant, p_w = "LINEAIR", "ref_lin", np.nan
        if not backtestbaar:
            label, variant = "GEPOOLD", "pooled"
        else:
            kand = min(("ridge", "gbm"), key=lambda k: mae[k] if np.isfinite(mae[k]) else 9e9)
            def wint(k):
                pr = paren(k)
                if len(pr) < 60:
                    return False, np.nan
                d = pr[:, 0] - pr[:, 1]
                t = d.mean() / (d.std(ddof=1) / math.sqrt(len(d)) + 1e-12)
                p = math.erfc(abs(t) / math.sqrt(2))
                marge = mae["ref_lin"] - mae[k]
                return (marge >= 0.03 and marge >= 0.02 * mae["ref_lin"] and p < 0.05), p
            ok, p_w = wint(kand)
            if ok:
                label, variant = "ML", kand
            else:
                ok_p, p_p = wint("pooled")
                if ok_p:
                    label, variant, p_w = "GEPOOLD", "pooled", p_p
        lab_telling[label] = lab_telling.get(label, 0) + 1

        # NGR-spreiding op out-of-sample-fouten van de gekozen variant
        e_sp = [(float(r[variant]) - float(r["doel"]),
                 kol["mm_spreiding"][datums.index(r["datum"])])
                for r in rs if r.get(variant)]
        e_sp = [(e, sp) for e, sp in e_sp if np.isfinite(sp)]
        c_b = d_b = crps_n = crps_c = np.nan
        if len(e_sp) >= 100:
            e = np.array([x[0] for x in e_sp]); sp = np.array([x[1] for x in e_sp])
            s0 = float(e.std(ddof=1)); crps_c = float(crps_gauss(e, np.full(len(e), s0)))
            best = (9e9, np.nan, np.nan)
            for c in np.arange(0.05, 2.51, 0.05):
                for dd in np.arange(0.0, 2.51, 0.05):
                    v = crps_gauss(e, np.sqrt(c * c + (dd * sp) ** 2))
                    if v < best[0]:
                        best = (v, c, dd)
            crps_n, c_b, d_b = float(best[0]), float(best[1]), float(best[2])

        # eindmodel op alle data hertrainen en exporteren
        tr = np.where(geldig)[0]
        y = kol["doel"][tr]
        exp = {"stad": naam, "icao": s["icao"], "label": label, "variant": variant,
               "eenheid_training": "°C", "ngr": {"c": c_b, "d": d_b}}
        if variant == "ref_lin" or label == "LINEAIR":
            co = ols(np.column_stack([kol["mm_gem"][tr], kol["lag2_err"][tr]]), y)
            exp["ref_lin"] = {"a": round(float(co[0]), 4), "b": round(float(co[1]), 4),
                              "g": round(float(co[2]), 4)}
        if label == "ML":
            X, med = matrix(kol, tr, feats)
            if variant == "ridge":
                mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1
                ri = Ridge(alpha=1.0).fit((X - mu) / sd, y)
                exp["ridge"] = {"features": feats, "mu": mu.round(4).tolist(),
                                "sd": sd.round(4).tolist(), "med": med.round(4).tolist(),
                                "coef": ri.coef_.round(5).tolist(),
                                "intercept": round(float(ri.intercept_), 4)}
            else:
                gb = HistGradientBoostingRegressor(
                    max_iter=120, learning_rate=0.07, max_leaf_nodes=15,
                    min_samples_leaf=20, l2_regularization=1.0, random_state=1).fit(X, y)
                pickle.dump({"model": gb, "features": feats, "med": med},
                            open(MODDIR / f"gbm_{key}.pkl", "wb"))
                exp["gbm_bestand"] = f"gbm_{key}.pkl"
        ml_export[key] = exp
        rd = lambda v: ("" if not np.isfinite(v) else round(v, 3))
        res.append([naam, s["icao"], "°F" if s["eenheid"] == "F" else "°C",
                    n_train, n_test, rd(mae["ruw"]), rd(mae["ref_lin"]), rd(mae["ridge"]),
                    rd(mae["gbm"]), rd(mae["pooled"]),
                    ("ML" if label == "ML" else label), variant, rd(p_w),
                    rd(crps_c), rd(crps_n), rd(c_b), rd(d_b)])

    # gepoold eindmodel op alle data
    extra = {s["key"]: (s["lat"], abs(s["lat"]), s["lon"], i) for i, s in enumerate(STEDEN)}
    Xp, yp = [], []
    for s in STEDEN:
        datums, kol = data[s["key"]]
        tr = np.where(np.isfinite(kol["mm_gem"]) & np.isfinite(kol["doel"]))[0]
        X, _ = matrix(kol, tr, feats)
        Xp.append(np.column_stack([X] + [np.full(len(tr), v) for v in extra[s["key"]]]))
        yp.append(kol["doel"][tr])
    Xp = np.vstack(Xp); yp = np.concatenate(yp)
    pooled = HistGradientBoostingRegressor(
        max_iter=150, learning_rate=0.07, max_leaf_nodes=31, min_samples_leaf=40,
        l2_regularization=1.0, categorical_features=[Xp.shape[1] - 1], random_state=1).fit(Xp, yp)
    pickle.dump({"model": pooled, "features": feats + ["lat", "lat_abs", "lon", "stad_idx"],
                 "stad_idx": {s["key"]: i for i, s in enumerate(STEDEN)}},
                open(MODDIR / "pooled_gbm.pkl", "wb"))
    json.dump(ml_export, open(MODDIR / "modellen.json", "w"), ensure_ascii=False, indent=1)

    with open(HIER / "resultaten.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stad", "icao", "markt_eenheid", "n_train", "n_test",
                    "mae_ruw", "mae_ref_lin", "mae_ridge", "mae_gbm", "mae_pooled",
                    "label", "gekozen_variant", "p_waarde",
                    "crps_constant", "crps_ngr", "ngr_c", "ngr_d"])
        w.writerows(res)
    print("labels:", lab_telling)
    print(f"resultaten.csv + modellen/ geschreven ({len(res)} steden)")

if __name__ == "__main__":
    (train if (sys.argv[1:] or ["train"])[0] == "train" else rapport)()
