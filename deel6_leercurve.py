#!/usr/bin/env python3
"""
Deel 4 · stap 3 als gecontroleerd experiment.

Gepoold neuraal netwerk (MLP, twee verborgen lagen) over alle 51 steden met
stads-one-hot als embedding, zelfde features en zelfde walk-forward als deel 3
(maandelijks bijtrainen, testen jan 2025 t/m jul 2026). Hervatbaar per maand.

  train   : voorspellingen_nn.csv aanvullen (checkpoint klaar_nn.json)
  rapport : per stad vergelijken met ref_lin en ridge (zelfde ML-beslisregel),
            plus CRPS-vergelijking via de NGR-spreidingsfit
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
from sklearn.neural_network import MLPRegressor
from scipy.special import erf as _erf

from deel3_train import laad_stad, matrix, P1, AUX, MAANDEN, STEDEN, HIER

FEATS  = P1 + ["mm_spreiding", "run2run", "doy_sin", "doy_cos", "lag2_err"] + AUX
VNN    = HIER / "voorspellingen_nn.csv"
KLAARN = HIER / "klaar_nn.json"

def crps_gauss(e, s):
    z = e / s
    Phi = 0.5 * (1 + _erf(z / math.sqrt(2)))
    phi = np.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    return np.mean(s * (z * (2 * Phi - 1) + 2 * phi - 1 / math.sqrt(math.pi)))

def train():
    data  = {s["key"]: laad_stad(s["key"]) for s in STEDEN}
    extra = {s["key"]: (s["lat"], abs(s["lat"]), s["lon"]) for s in STEDEN}
    idx_s = {s["key"]: i for i, s in enumerate(STEDEN)}
    naam  = {s["key"]: s["naam"] for s in STEDEN}
    n_cont = len(FEATS) + 3          # continue kolommen die geschaald worden

    klaar = json.load(open(KLAARN)) if KLAARN.exists() else []
    nieuw = not VNN.exists()
    fu = open(VNN, "a", newline=""); w = csv.writer(fu)
    if nieuw:
        w.writerow(["maand", "stad", "datum", "doel", "nn"])

    for maand in MAANDEN:
        if maand in klaar:
            continue
        grens = maand + "-01"
        Xtr, ytr, blokken = [], [], {}
        for key, (datums, kol) in data.items():
            da = np.array(datums)
            geldig = np.isfinite(kol["mm_gem"]) & np.isfinite(kol["doel"])
            tr = np.where(geldig & (da < grens))[0]
            te = np.where(geldig & np.char.startswith(da, maand))[0]
            if len(tr):
                X, med = matrix(kol, tr, FEATS)
                one = np.zeros((len(tr), len(STEDEN))); one[:, idx_s[key]] = 1
                Xtr.append(np.column_stack(
                    [X] + [np.full(len(tr), v) for v in extra[key]] + [one]))
                ytr.append(kol["doel"][tr])
                blokken[key] = (te, med)
        Xtr = np.vstack(Xtr); ytr = np.concatenate(ytr)
        if len(ytr) < 2000:
            klaar.append(maand); json.dump(klaar, open(KLAARN, "w")); continue
        mu = Xtr[:, :n_cont].mean(0); sd = Xtr[:, :n_cont].std(0); sd[sd == 0] = 1
        Xtr[:, :n_cont] = (Xtr[:, :n_cont] - mu) / sd
        nn = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu",
                          alpha=1e-4, learning_rate_init=1e-3, batch_size=256,
                          max_iter=250, early_stopping=True, validation_fraction=0.1,
                          n_iter_no_change=12, random_state=1)
        nn.fit(Xtr, ytr)

        n_rij = 0
        for key, (datums, kol) in data.items():
            te, med = blokken.get(key, (np.array([], dtype=int), None))
            if not len(te):
                continue
            X, _ = matrix(kol, te, FEATS, med)
            one = np.zeros((len(te), len(STEDEN))); one[:, idx_s[key]] = 1
            Xe = np.column_stack([X] + [np.full(len(te), v) for v in extra[key]] + [one])
            Xe[:, :n_cont] = (Xe[:, :n_cont] - mu) / sd
            yv = nn.predict(Xe)
            for i, ix in enumerate(te):
                w.writerow([maand, naam[key], datums[ix],
                            round(float(kol["doel"][ix]), 2), round(float(yv[i]), 2)])
                n_rij += 1
        fu.flush()
        klaar.append(maand); json.dump(klaar, open(KLAARN, "w"))
        print(f"  {maand}: {n_rij} nn-testdagen  (train {len(ytr)} rijen, "
              f"{nn.n_iter_} epochs)", flush=True)
    fu.close()
    print("nn-train klaar:", len(klaar), "maanden")

def rapport():
    basis = {(r["stad"], r["datum"]): r for r in csv.DictReader(open(HIER / "voorspellingen.csv"))}
    nn    = list(csv.DictReader(open(VNN)))
    data  = {s["naam"]: laad_stad(s["key"]) for s in STEDEN}

    def toets(paren):
        """(fout_ref, fout_kand) per dag → (wint volgens ML-regel, p, mae_ref, mae_k)"""
        pr = np.array(paren)
        if len(pr) < 60:
            return False, np.nan, np.nan, np.nan
        m_ref, m_k = pr[:, 0].mean(), pr[:, 1].mean()
        d = pr[:, 0] - pr[:, 1]
        t = d.mean() / (d.std(ddof=1) / math.sqrt(len(d)) + 1e-12)
        p = math.erfc(abs(t) / math.sqrt(2))
        marge = m_ref - m_k
        return (marge >= 0.03 and marge >= 0.02 * m_ref and p < 0.05), p, m_ref, m_k

    rijen_uit, telling = [], {"nn_wint_van_ref": 0, "nn_wint_van_ridge": 0,
                              "ridge_wint_van_nn": 0}
    crps_nn_all, crps_ri_all = [], []
    for s in STEDEN:
        naam = s["naam"]
        p_ref, p_ri, e_nn, e_ri = [], [], [], []
        for r in nn:
            if r["stad"] != naam:
                continue
            b = basis.get((naam, r["datum"]))
            if not (b and b["doel"] and r["nn"]):
                continue
            doel = float(b["doel"]); v_nn = float(r["nn"])
            if b["ref_lin"]:
                p_ref.append((abs(float(b["ref_lin"]) - doel), abs(v_nn - doel)))
            if b["ridge"]:
                p_ri.append((abs(float(b["ridge"]) - doel), abs(v_nn - doel)))
                datums, kol = data[naam]
                sp = kol["mm_spreiding"][datums.index(r["datum"])]
                if np.isfinite(sp):
                    e_nn.append((v_nn - doel, sp))
                    e_ri.append((float(b["ridge"]) - doel, sp))
        w_ref, p1v, m_ref, m_nn = toets(p_ref)
        w_ri,  p2v, m_ri,  _    = toets(p_ri)
        ri_wint, _, _, _ = toets([(b, a) for a, b in p_ri])
        telling["nn_wint_van_ref"]   += int(w_ref)
        telling["nn_wint_van_ridge"] += int(w_ri)
        telling["ridge_wint_van_nn"] += int(ri_wint)

        def ngr_crps(paren):
            e = np.array([x[0] for x in paren]); sp = np.array([x[1] for x in paren])
            best = 9e9
            for c in np.arange(0.05, 2.51, 0.05):
                for dd in np.arange(0.0, 2.51, 0.05):
                    v = crps_gauss(e, np.sqrt(c * c + (dd * sp) ** 2))
                    if v < best:
                        best = v
            return float(best)
        c_nn = ngr_crps(e_nn) if len(e_nn) >= 100 else np.nan
        c_ri = ngr_crps(e_ri) if len(e_ri) >= 100 else np.nan
        if np.isfinite(c_nn): crps_nn_all.append(c_nn)
        if np.isfinite(c_ri): crps_ri_all.append(c_ri)
        rd = lambda v: ("" if not np.isfinite(v) else round(v, 3))
        rijen_uit.append([naam, len(p_ri), rd(m_ref), rd(m_ri), rd(m_nn),
                          int(w_ref), int(w_ri), rd(p2v), rd(c_ri), rd(c_nn)])

    with open(HIER / "resultaten_nn.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stad", "n_test", "mae_ref_lin", "mae_ridge", "mae_nn",
                    "nn_haalt_ml_drempel_vs_ref", "nn_verslaat_ridge",
                    "p_nn_vs_ridge", "crps_ridge", "crps_nn"])
        w.writerows(rijen_uit)
    mae = lambda k: np.nanmean([float(r[k]) for r in rijen_uit if r[k] != ""]
                               if False else [x[ {"ref":2,"ri":3,"nn":4}[k] ] for x in rijen_uit if x[{"ref":2,"ri":3,"nn":4}[k]] != ""])
    print("gemiddelde MAE (°C): ref_lin",
          round(float(np.mean([x[2] for x in rijen_uit if x[2] != ""])), 3),
          "· ridge", round(float(np.mean([x[3] for x in rijen_uit if x[3] != ""])), 3),
          "· nn", round(float(np.mean([x[4] for x in rijen_uit if x[4] != ""])), 3))
    print("telling:", telling)
    if crps_nn_all and crps_ri_all:
        print("gemiddelde CRPS: ridge", round(float(np.mean(crps_ri_all)), 3),
              "· nn", round(float(np.mean(crps_nn_all)), 3))
    print("resultaten_nn.csv geschreven")

if __name__ == "__main__":
    (train if (sys.argv[1:] or ["train"])[0] == "train" else rapport)()
