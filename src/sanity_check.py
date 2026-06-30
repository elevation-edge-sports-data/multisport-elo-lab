import pandas as pd

df = pd.read_csv("outputs/backtest_BASE.csv")

print("Probability bounds check:")
print(df.p_home.min(), df.p_home.max())

print("\nElo sanity check:")
print(df[["home_elo_post", "away_elo_post"]].describe())

print("\nMissing values:")
print(df.isnull().sum())