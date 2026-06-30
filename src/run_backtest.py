import os
import pandas as pd

from src.elo_engine import (
    INITIAL_ELO,
    win_prob,
    update_elo
)

from src.models.mov import mov_multiplier
from src.models.hfa import DEFAULT_HFA

# =========================
# LOAD DATA
# =========================

os.makedirs("outputs", exist_ok=True)

# =========================
# MODEL CONFIGURATION
# =========================

MODEL_CONFIG = {

    "BASE": {
        "use_mov": False,
        "use_hfa": False,
        "k": 20,
        "hfa": 0
    },

    "MOV": {
        "use_mov": True,
        "use_hfa": False,
        "k": 20,
        "hfa": 0
    },

    "HFA": {
        "use_mov": False,
        "use_hfa": True,
        "k": 20,
        "hfa": DEFAULT_HFA
    },

    "MOV_HFA": {
        "use_mov": True,
        "use_hfa": True,
        "k": 20,
        "hfa": DEFAULT_HFA
    }

}


# =========================
# BACKTEST FUNCTION
# =========================

def run_backtest(config, model_name):

    df = pd.read_csv("data/nfl_games.csv")
    df = df.sort_values(["season", "week"]).reset_index(drop=True)

    team_elo = {}

    def get_elo(team):
        return team_elo.get(team, INITIAL_ELO)

    def set_elo(team, value):
        team_elo[team] = value

    results = []

    for _, row in df.iterrows():

        home = row["home_team"]
        away = row["away_team"]

        home_score = row["home_score"]
        away_score = row["away_score"]

        home_elo = get_elo(home)
        away_elo = get_elo(away)

        actual = int(home_score > away_score)

        # -------------------------
        # Configure prediction
        # -------------------------

        adjusted_home = home_elo

        if config["use_hfa"]:
            adjusted_home += config["hfa"]

        multiplier = 1.0

        if config["use_mov"]:
            multiplier = mov_multiplier(
                home_score,
                away_score
            )

        # -------------------------
        # Prediction
        # -------------------------

        p_home = win_prob(
            adjusted_home,
            away_elo
        )

        # -------------------------
        # Elo update
        # -------------------------

        home_elo_new, away_elo_new = update_elo(
            home_elo=home_elo,
            away_elo=away_elo,
            actual=actual,
            p_home=p_home,
            k=config["k"],
            multiplier=multiplier
        )

        # -------------------------
        # Store results
        # -------------------------

        results.append({

            "home_team": home,
            "away_team": away,

            "season": row["season"],
            "week": row["week"],

            "home_elo_pre": home_elo,
            "away_elo_pre": away_elo,

            "p_home": p_home,
            "actual": actual,

            "home_elo_post": home_elo_new,
            "away_elo_post": away_elo_new,

            "model": model_name

        })

        set_elo(home, home_elo_new)
        set_elo(away, away_elo_new)

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        f"outputs/backtest_{model_name}.csv",
        index=False
    )

    print("Backtest complete:", model_name)

    return results_df


# =========================
# COMMAND LINE ENTRY POINT
# =========================

if __name__ == "__main__":

    for MODEL in ["BASE", "MOV", "HFA", "MOV_HFA"]:

        run_backtest(
            MODEL_CONFIG[MODEL],
            MODEL
        )