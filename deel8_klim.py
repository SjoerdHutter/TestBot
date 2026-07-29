#!/usr/bin/env python3
"""
Deel 6 · leercurve: hoe schaalt de fout met de hoeveelheid trainingsdata?

Vaste testset: 1 jan t/m 28 jul 2026, alle 51 steden. Training telkens op de
laatste N dagen vóór 2026 (N = 120, 240, 360, 480, alles ≈ 660). Per venster:
  ridge   per stad (de huidige kampioen)
  gbm     gepoold HistGradientBoosting
  nn      gepoold MLP 64×32 met stads-one-hot
Uitvoer: leercurve.csv. Hervatbaar: al berekende vensters worden overgeslagen.
Daarna een 1/√n-extrapolatie als indicatie voor 25 jaar (n ≈ 9400 per station),
met de kanttekening dat dit een bovengrens is (niet-stationariteit oude modellen).
"""
import csv, math, sys
from datetime import date, timedelta
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor

from deel3_train import laad_stad, matrix, P1, AUX, STEDEN, HIER

FEATS   = P1 + ["mm_spreiding", "run2run", "doy_sin", "doy_cos", "lag2_err"] + AUX
UIT     = HIER / "leercurve.csv"
GRENS   = "2026-01-01"
VENSTERS = [120, 240, 360, 480, 9999]

def run():
    data  = {s["key"]: laad_stad(s["key"]) for s in STEDEN}
    extra = {s["key"]: (s["lat"], abs(s["lat"]), s["lon"]) for s in STEDEN}
    idx_s = {s["key"]: i for i, s in enumerate(STEDEN)}

    klaar = set()
    if UIT.exists():
        klaar = {int(r["venster_dagen"]) for r in csv.DictReader(open(UIT))}
    else:
        with open(UIT, "w", newline="") as f:
            csv.writer(f).writerow(["venster_dagen", "n_train_totaal",
                                    "mae_ridge", "mae_gbm", "mae_nn"])

    for venster in VENSTERS:
        if venster in klaar:
            continue
        vanaf = (date.fromisoformat(GRENS) - timedelta(days=venster)).isoformat()
        fouten = {"ridge": [], "gbm": [], "nn": []}
        Xg, yg, Xn, yn, blokken = [], [], [], [], {}
        for key, (datums, kol) in data.items():
            da = np.array(datums)
            geldig = np.isfinite(kol["mm_gem"]) & np.isfinite(kol["doel"])
            tr = np.where(geldig & (da < GRENS) & (da >= vanaf))[0]
            te = np.where(geldig & (da >= GRENS))[0]
            if len(tr) < 60 or not len(te):
                continue
            X_tr, med = matrix(kol, tr, FEATS)
            X_te, _   = matrix(kol, te, FEATS, med)
            y_tr, y_te = kol["doel"][tr], kol["doel"][te]
            mu, sd = X_tr.mean(0), X_tr.std(0); sd[sd == 0] = 1
            ri = Ridge(alpha=1.0).fit((X_tr - mu) / sd, y_tr)
            fouten["ridge"].extend(np.abs(ri.predict((X_te - mu) / sd) - y_te))
            ex = [np.full(len(tr), v) for v in extra[key]]
            Xg.append(np.column_stack([X_tr] + ex + [np.full(len(tr), idx_s[key])]))
            one = np.zeros((len(tr), len(STEDEN))); one[:, idx_s[key]] = 1
            Xn.append(np.column_stack([X_tr] + ex + [one]))
            yg.append(y_tr); yn.append(y_tr)
            blokken[key] = (te, med, X_te, y_te)

        Xg = np.vstack(Xg); yg = np.concatenate(yg)
        Xn = np.vstack(Xn); yn = np.concatenate(yn)
        n_cont = len(FEATS) + 3
        gb = HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.07, max_leaf_nodes=31, min_samples_leaf=40,
            l2_regularization=1.0, categorical_features=[Xg.shape[1] - 1],
            random_state=1).fit(Xg, yg)
        mu_n = Xn[:, :n_cont].mean(0); sd_n = Xn[:, :n_cont].std(0); sd_n[sd_n == 0] = 1
        Xn[:, :n_cont] = (Xn[:, :n_cont] - mu_n) / sd_n
        nn = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", alpha=1e-4,
                          learning_rate_init=1e-3, batch_size=256, max_iter=250,
                          early_stopping=True, validation_fraction=0.1,
                          n_iter_no_change=12, random_state=1).fit(Xn, yn)

        for key, (te, med, X_te, y_te) in blokken.items():
            ex = [np.full(len(te), v) for v in extra[key]]
            Xg_te = np.column_stack([X_te] + ex + [np.full(len(te), idx_s[key])])
            fouten["gbm"].extend(np.abs(gb.predict(Xg_te) - y_te))
            one = np.zeros((len(te), len(STEDEN))); one[:, idx_s[key]] = 1
            Xn_te = np.column_stack([X_te] + ex + [one])
            Xn_te[:, :n_cont] = (Xn_te[:, :n_cont] - mu_n) / sd_n
            fouten["nn"].extend(np.abs(nn.predict(Xn_te) - y_te))

        rij = [venster, len(yg)] + [round(float(np.mean(fouten[k])), 4)
                                    for k in ("ridge", "gbm", "nn")]
        with open(UIT, "a", newline="") as f:
            csv.writer(f).writerow(rij)
        print(f"  venster {venster:>4} d · train {len(yg):>6} rijen · "
              f"MAE ridge {rij[2]} · gbm {rij[3]} · nn {rij[4]}", flush=True)

    # ── extrapolatie: MAE(n) = a + b/√n per modelfamilie ─────────────────────
    rijen = sorted(csv.DictReader(open(UIT)), key=lambda r: int(r["venster_dagen"]))
    rijen = [r for r in rijen if int(r["venster_dagen"]) >= 360]
    print("\nExtrapolatie op vensters ≥ 360 dagen (kortere missen hele seizoenen en")
    print("meten seizoensdekking i.p.v. steekproefomvang). a + b/√n; indicatie, bovengrens:")
    for k in ("ridge", "gbm", "nn"):
        n  = np.array([min(int(r["venster_dagen"]), 660) for r in rijen], float)
        ma = np.array([float(r[f"mae_{k}"]) for r in rijen])
        A  = np.column_stack([np.ones(len(n)), 1 / np.sqrt(n)])
        co, *_ = np.linalg.lstsq(A, ma, rcond=None)
        v25 = co[0] + co[1] / math.sqrt(9400)
        print(f"  {k:<6} asymptoot a = {co[0]:.3f} °C · bij 25 jaar ≈ {v25:.3f} °C "
              f"(nu {ma[-1]:.3f})".replace(".", ","))

if __name__ == "__main__":
    run()
