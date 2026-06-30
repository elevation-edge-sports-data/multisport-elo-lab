import pandas as pd
import numpy as np
import os

from src.elo_engine import win_prob, update_elo
from src.models.mov import mov_multiplier
from src.models.hfa import HFA
from src.elo_engine import INITIAL_ELO

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("data/nfl_games.csv")
df = df.sort_values(["season", "week"]).reset_index(drop=True)

# =========================
# STATE
# =========================

team_elo = {}

def get_elo(team):
    return team_elo.get(team, INITIAL_ELO)

def set_elo(team, value):
    team_elo[team] = value

# =========================
# STORAGE
# =========================

results = []

# =========================
# MODEL SELECTOR
# =========================

MODEL = "HFA"
# MODEL = "MOV"
# MODEL = "BASE"
# MODEL = os.getenv("MODEL", "BASE")
  # BASE | MOV | HFA

# =========================
# BACKTEST LOOP
# =========================

for _, row in df.iterrows():

    home = row["home_team"]
    away = row["away_team"]

    home_score = row["home_score"]
    away_score = row["away_score"]

    home_elo = get_elo(home)
    away_elo = get_elo(away)

    # =========================
    # PREDICTION STEP
    # =========================

    if MODEL == "BASE":

        p_home = win_prob(home_elo, away_elo)

        error = (1 if home_score > away_score else 0) - p_home

        home_elo_new = home_elo + 20 * error
        away_elo_new = away_elo - 20 * error

        mov_factor = 1.0

    elif MODEL == "MOV":

        margin = abs(home_score - away_score)
        mov_factor = np.log(margin + 1)

        p_home = win_prob(home_elo, away_elo)

        error = (1 if home_score > away_score else 0) - p_home

        home_elo_new = home_elo + 20 * error * mov_factor
        away_elo_new = away_elo - 20 * error * mov_factor

    elif MODEL == "HFA":

        adjusted_home = home_elo + HFA

        p_home = win_prob(adjusted_home, away_elo)

        error = (1 if home_score > away_score else 0) - p_home

        home_elo_new = home_elo + 20 * error
        away_elo_new = away_elo - 20 * error

        mov_factor = 1.0

    else:
        raise ValueError("Invalid MODEL")

    # =========================
    # STORE RESULTS
    # =========================

    actual = 1 if home_score > away_score else 0

    results.append({
        "home_team": home,
        "away_team": away,
        "week": row["week"],
        "season": row["season"],

        "home_elo_pre": home_elo,
        "away_elo_pre": away_elo,

        "p_home": p_home,
        "actual": actual,

        "home_elo_post": home_elo_new,
        "away_elo_post": away_elo_new,

        "model": MODEL
    })

    # =========================
    # UPDATE STATE
    # =========================

    set_elo(home, home_elo_new)
    set_elo(away, away_elo_new)

# =========================
# OUTPUT
# =========================

results_df = pd.DataFrame(results)
results_df.to_csv(f"outputs/backtest_{MODEL}.csv", index=False)

print("Backtest complete:", MODEL)