"""
Parameter optimization workflow.

Evaluates multiple Elo parameter combinations by running
historical backtests and comparing predictive performance.
"""

import os
import pandas as pd

from elo_lab.workflows.run_backtest import run_backtest
from elo_lab.configuration.model_configs import MODEL_CONFIGS

from elo_lab.evaluation.metrics import accuracy, log_loss, brier

os.makedirs("outputs", exist_ok=True)

# =========================
# PARAMETER GRID
# =========================

K_VALUES = [10, 15, 20, 25, 30]
HFA_VALUES = [20, 35, 50, 65, 80]

BASE_MODEL = "MOV_HFA"

# =========================
# GRID SEARCH
# =========================

results = []

for k in K_VALUES:
    for hfa in HFA_VALUES:

        # Update the model configuration for the current
        # grid-search iteration.
        config = MODEL_CONFIGS[BASE_MODEL].copy()
        config["k"] = k

        config.setdefault("adjustments", {})
        config["adjustments"].setdefault("home_field", {})
        config["adjustments"]["home_field"]["value"] = hfa

        label = f"MOV_HFA_k{k}_hfa{hfa}"

        print(f"Running: {label}")

        df = run_backtest(config, label)

        p = df["p_home"].astype(float).values
        y = df["actual"].astype(int).values

        results.append({
            "model": BASE_MODEL,
            "k": k,
            "hfa": hfa,
            "accuracy": float(accuracy(p, y)),
            "log_loss": float(pd.Series(log_loss(p, y)).mean()),
            "brier": float(pd.Series(brier(p, y)).mean()),
        })

# =========================
# SAVE RESULTS
# =========================

results_df = (
    pd.DataFrame(results)
    .sort_values("accuracy", ascending=False)
    .reset_index(drop=True)
)

results_df.to_csv("outputs/parameter_search.csv", index=False)

print(results_df.head(10))