"""
Model evaluation workflow.

Aggregates historical backtest results and computes
predictive performance metrics for each model.
"""

import os
import pandas as pd

from elo_lab.evaluation.metrics import accuracy, log_loss, brier

os.makedirs("outputs", exist_ok=True)

# =========================
# FIND BACKTEST FILES
# =========================

files = sorted(os.listdir("outputs"))

backtest_files = [
    f for f in files
    if f.startswith("backtest_") and f.endswith(".csv")
]

# =========================
# EVALUATE MODELS
# =========================

model_summary = []

for filename in backtest_files:

    model = filename.replace("backtest_", "").replace(".csv", "")

    df = pd.read_csv(os.path.join("outputs", filename))

    df["log_loss"] = df.apply(lambda r: log_loss(r.p_home, r.actual), axis=1)
    df["brier"] = df.apply(lambda r: brier(r.p_home, r.actual), axis=1)

    model_summary.append({
        "model": model,
        "accuracy": accuracy(df.p_home.values, df.actual.values),
        "log_loss": df["log_loss"].mean(),
        "brier": df["brier"].mean(),
    })

# =========================
# SAVE MODEL COMPARISON
# =========================

comparison = pd.DataFrame(model_summary)

# Present results in a consistent model order.
comparison = comparison.sort_values("model").reset_index(drop=True)

comparison.to_csv("outputs/model_comparison.csv", index=False)

print(comparison)