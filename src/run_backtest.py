import os
import pandas as pd

from src.elo_engine import (
    INITIAL_ELO,
    win_prob,
    update_elo
)

from src.models.mov import mov_multiplier
from src.models.hfa import HFA

# =========================
# LOAD DATA
# =========================

os.makedirs("outputs", exist_ok=True)

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

MODEL = "BASE"
# MODEL = "MOV"
# MODEL = "HFA"

# =========================
# MODEL CONFIGURATION
# =========================

MODEL_CONFIG = {

    "BASE": {
        "use_hfa": False,
        "use_mov": False
    },

    "MOV": {
        "use_hfa": False,
        "use_mov": True
    },

    "HFA": {
        "use_hfa": True,
        "use_mov": False
    }

}

if MODEL not in MODEL_CONFIG:
    raise ValueError(f"Unknown model: {MODEL}")

config = MODEL_CONFIG[MODEL]

# =========================
# BACKTEST LOOP
# =========================

for _, row in df.iterrows():

    home = row["home_team"]
    away = row["away_team"]

    home_score = row["home_score"]
    away_score = row["away_score"]

    actual = int(home_score > away_score)

    home_elo = get_elo(home)
    away_elo = get_elo(away)

    # -------------------------
    # Apply Home Field Advantage
    # -------------------------

    adjusted_home = home_elo

    if config["use_hfa"]:
        adjusted_home += HFA

    # -------------------------
    # Compute Win Probability
    # -------------------------

    p_home = win_prob(
        adjusted_home,
        away_elo
    )

    # -------------------------
    # Margin of Victory
    # -------------------------

    multiplier = 1.0

    if config["use_mov"]:
        multiplier = mov_multiplier(
            home_score,
            away_score
        )

    # -------------------------
    # Elo Update
    # -------------------------

    home_elo_new, away_elo_new = update_elo(
        home_elo,
        away_elo,
        actual,
        p_home,
        multiplier
    )

    # -------------------------
    # Store Results
    # -------------------------

    results.append({

        "season": row["season"],
        "week": row["week"],

        "home_team": home,
        "away_team": away,

        "home_elo_pre": home_elo,
        "away_elo_pre": away_elo,

        "p_home": p_home,
        "actual": actual,

        "home_elo_post": home_elo_new,
        "away_elo_post": away_elo_new,

        "model": MODEL

    })

    set_elo(home, home_elo_new)
    set_elo(away, away_elo_new)

# =========================
# OUTPUT
# =========================

results_df = pd.DataFrame(results)

results_df.to_csv(
    f"outputs/backtest_{MODEL}.csv",
    index=False
)

print("Backtest complete:", MODEL)