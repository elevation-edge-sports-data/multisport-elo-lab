import random
import pandas as pd
from collections import defaultdict

from src.elo_engine import (
    INITIAL_ELO,
    win_prob,
    update_elo,
)

from src.models.hfa import DEFAULT_HFA


# =========================
# DEFAULT CONFIG
# =========================

DEFAULT_CONFIG = {
    "k": 20,
    "hfa": DEFAULT_HFA,
    "use_hfa": True,
    "use_mov": False,
}


# =========================
# SIMULATE ONE GAME
# =========================

def simulate_game(
    home_elo,
    away_elo,
    config=None,
    rng=None,
):
    if config is None:
        config = DEFAULT_CONFIG

    if rng is None:
        rng = random

    adjusted_home = home_elo + (config["hfa"] if config["use_hfa"] else 0.0)

    p_home = win_prob(adjusted_home, away_elo)

    random_draw = rng.random()
    actual = int(random_draw < p_home)

    home_new, away_new = update_elo(
        home_elo=home_elo,
        away_elo=away_elo,
        actual=actual,
        p_home=p_home,
        k=config["k"],
        multiplier=1.0,
    )

    return {
        "p_home": float(p_home),
        "random_draw": float(random_draw),
        "actual": int(actual),
        "home_elo_post": float(home_new),
        "away_elo_post": float(away_new),
    }


# =========================
# SIMULATE ONE SEASON
# =========================

def simulate_season(
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
):
    if config is None:
        config = DEFAULT_CONFIG

    rng = random.Random(seed)

    schedule = pd.read_csv(schedule_path)

# KEEP ONLY REGULAR SEASON GAMES
    schedule = schedule[schedule["week"] <= 18]

    schedule = schedule.sort_values(["season", "week"]).reset_index(drop=True)  
    
    teams = sorted(set(schedule["home_team"]).union(schedule["away_team"]))

    team_elo = {t: INITIAL_ELO for t in teams}
    wins = {t: 0 for t in teams}
    losses = {t: 0 for t in teams}

    for _, game in schedule.iterrows():
        home = game["home_team"]
        away = game["away_team"]

        result = simulate_game(
            home_elo=team_elo[home],
            away_elo=team_elo[away],
            config=config,
            rng=rng,
        )

        team_elo[home] = result["home_elo_post"]
        team_elo[away] = result["away_elo_post"]

        if result["actual"] == 1:
            wins[home] += 1
            losses[away] += 1
        else:
            wins[away] += 1
            losses[home] += 1

    standings = pd.DataFrame({
        "team": teams,
        "wins": [wins[t] for t in teams],
        "losses": [losses[t] for t in teams],
    }).sort_values(
        ["wins", "losses", "team"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    elo_df = pd.DataFrame({
        "team": teams,
        "elo": [team_elo[t] for t in teams],
    }).sort_values(
        "elo",
        ascending=False,
    ).reset_index(drop=True)

    return standings, elo_df


# =========================
# 4C: MONTE CARLO ENGINE
# =========================

def simulate_many_seasons(
    n_sims=1000,
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
):
    if config is None:
        config = DEFAULT_CONFIG

    results = []

    for sim in range(n_sims):
        standings, _ = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + sim,
        )

        for _, row in standings.iterrows():
            results.append({
                "sim_id": sim,
                "team": row["team"],
                "wins": int(row["wins"]),
            })

    return pd.DataFrame(results)


# =========================
# 4D: SUMMARY STATISTICS
# =========================

def summarize_simulations(sim_df):
    summary = sim_df.groupby("team")["wins"].agg(
        mean="mean",
        std="std",
        min="min",
        max="max",
        median="median",
    ).reset_index()

    return summary.sort_values("mean", ascending=False)


# =========================
# 4E: WIN DISTRIBUTIONS
# =========================

def win_distributions(sim_df):
    dist = (
        sim_df.groupby(["team", "wins"])
        .size()
        .reset_index(name="count")
    )

    dist["probability"] = dist.groupby("team")["count"].transform(
        lambda x: x / x.sum()
    )

    return dist.sort_values(["team", "wins"])


# =========================
# PRINT HELPERS
# =========================

def print_standings(standings):
    print("\nFinal Standings")
    print("----------------")
    print(standings.to_string(index=False))


def print_elos(elo_df):
    print("\nFinal Elo Ratings")
    print("-----------------")
    print(elo_df.round({"elo": 1}).to_string(index=False))


# =========================
# DEMO
# =========================

if __name__ == "__main__":

    standings, elo_df = simulate_season()

    print_standings(standings)
    print_elos(elo_df)

    print("\nRunning Monte Carlo (4C)...")

    sim_df = simulate_many_seasons(n_sims=500)

    print("\nSummary (4D)")
    print(summarize_simulations(sim_df).head(10))

    print("\nWin distributions sample (4E)")
    print(win_distributions(sim_df).head(20))