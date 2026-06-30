from src.run_backtest import run_backtest, MODEL_CONFIG

config = MODEL_CONFIG["MOV_HFA"].copy()
config["k"] = 20
config["hfa"] = 20

df = run_backtest(config, "sanity_test")

print(df[["p_home", "actual"]].head(20))

print("p_home min:", df["p_home"].min())
print("p_home max:", df["p_home"].max())
print("NaNs:", df["p_home"].isna().sum())

print("unique actual values:", sorted(df["actual"].unique()))
print(df["p_home"].describe())