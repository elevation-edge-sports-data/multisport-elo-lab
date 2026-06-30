import pandas as pd
from src.eval.metrics_core import accuracy, log_loss, brier

models = ["BASE", "MOV", "HFA"]

summary = []

for m in models:

    df = pd.read_csv(f"outputs/backtest_{m}.csv")

    df["log_loss"] = df.apply(lambda r: log_loss(r.p_home, r.actual), axis=1)
    df["brier"] = df.apply(lambda r: brier(r.p_home, r.actual), axis=1)

    summary.append({
        "model": m,
        "accuracy": accuracy(df.p_home, df.actual),
        "log_loss": df.log_loss.mean(),
        "brier": df.brier.mean()
    })

summary_df = pd.DataFrame(summary)
summary_df.to_csv("outputs/model_comparison.csv", index=False)

print(summary_df)