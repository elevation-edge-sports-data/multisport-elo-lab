"""
Sanity checks for Elo model outputs.

Runs a quick backtest and prints diagnostic summaries of:
- probability outputs
- Elo ratings
- missing values
"""

import pandas as pd

from elo_lab.workflows.run_backtest import run_backtest
from elo_lab.configuration.model_configs import MODEL_CONFIGS

# =========================
# GENERATE TEST BACKTEST
# =========================

config = MODEL_CONFIGS["MOV_HFA"].copy()
config["k"] = 20
config["adjustments"]["home_field"]["value"] = 20

backtest = run_backtest(
    config=config,
    model_name="sanity_test"
)


# =========================
# PROBABILITY CHECKS
# =========================

print("\nProbability sample")
print("------------------")
print(backtest[["p_home", "actual"]].head(20))

print("\nProbability bounds")
print("------------------")
print(f"Min: {backtest['p_home'].min():.6f}")
print(f"Max: {backtest['p_home'].max():.6f}")

print("\nProbability summary")
print("-------------------")
print(backtest["p_home"].describe())

print("\nUnique actual values")
print("--------------------")
print(sorted(backtest["actual"].unique()))


# =========================
# ELO CHECKS
# =========================

print("\nElo summary")
print("-----------")
print(
    backtest[
        ["home_elo_post", "away_elo_post"]
    ].describe()
)


# =========================
# MISSING VALUES
# =========================

print("\nMissing values")
print("--------------")
print(backtest.isnull().sum())