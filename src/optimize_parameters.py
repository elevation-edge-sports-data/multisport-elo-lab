import pandas as pd

from src.run_backtest import run_backtest, MODEL_CONFIG
from src.eval.metrics_core import accuracy, log_loss, brier


# =========================
# PARAMETER GRID (Option A)
# =========================

k_values = [10, 15, 20, 25, 30]
hfa_values = [20, 35, 50, 65, 80]

BASE_MODEL = "MOV_HFA"

results = []


# =========================
# GRID SEARCH
# =========================

for k in k_values:
    for hfa in hfa_values:

        config = MODEL_CONFIG[BASE_MODEL].copy()
        config["k"] = k
        config["hfa"] = hfa

        label = f"MOV_HFA_k{k}_hfa{hfa}"

        print(f"Running: {label}")

        df = run_backtest(config, label)

        # -------------------------
        # FORCE SCALAR METRICS
        # -------------------------

        p = df["p_home"].astype(float).values
        y = df["actual"].astype(int).values
        acc = accuracy(p, y)
        ll = float(pd.Series(log_loss(p, y)).mean())
        br = float(pd.Series(brier(p, y)).mean())


        results.append({
            "model": BASE_MODEL,
            "k": k,
            "hfa": hfa,
            "accuracy": float(acc),
            "log_loss": ll,
            "brier": br
        })


# =========================
# RESULTS TABLE
# =========================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="accuracy",
    ascending=False
).reset_index(drop=True)


# =========================
# SAVE
# =========================

results_df.to_csv(
    "outputs/parameter_search.csv",
    index=False
)

print("\nTop 10 configurations:")
print(results_df.head(10))