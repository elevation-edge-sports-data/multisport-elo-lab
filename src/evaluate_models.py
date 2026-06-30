import os
import pandas as pd

from src.eval.metrics_core import accuracy, log_loss, brier

# =========================
# FIND ALL BACKTEST FILES
# =========================

files = sorted(os.listdir("outputs"))

backtest_files = [
    f for f in files
    if f.startswith("backtest_") and f.endswith(".csv")
]

# =========================
# EVALUATE EACH MODEL
# =========================

summary = []

for filename in backtest_files:

    model = filename.replace("backtest_", "").replace(".csv", "")

    df = pd.read_csv(os.path.join("outputs", filename))

    df["log_loss"] = df.apply(
        lambda r: log_loss(r.p_home, r.actual),
        axis=1
    )

    df["brier"] = df.apply(
        lambda r: brier(r.p_home, r.actual),
        axis=1
    )

    summary.append({

        "model": model,

        "accuracy": accuracy(
            df.p_home,
            df.actual
        ),

        "log_loss": df.log_loss.mean(),

        "brier": df.brier.mean()

    })

# =========================
# SAVE RESULTS
# =========================

summary_df = pd.DataFrame(summary)

summary_df = summary_df.sort_values("model").reset_index(drop=True)

summary_df.to_csv(
    "outputs/model_comparison.csv",
    index=False
)

print(summary_df)