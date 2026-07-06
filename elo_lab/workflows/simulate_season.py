"""
Season simulation workflow.

Simulates complete seasons using the Elo engine, supports
repeated Monte Carlo simulations, and summarizes simulated
season outcomes.
"""

import random
import pandas as pd

from elo_lab.engine.game_runner import run_game
from elo_lab.engine.constants import INITIAL_ELO

# Default Elo configuration used when no model configuration
# is supplied to the simulation workflow.
DEFAULT_CONFIG = {
    "k": 20,
    "adjustments": {
        "home_field": {"enabled": True, "value": 55},
        "margin_of_victory": {"enabled": False}
    }
}

# =========================
# SINGLE SEASON SIMULATION
# =========================

def simulate_season(
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
):
    """
    Simulates a single regular season using the configured Elo model
    and returns final standings and Elo ratings.
    """
    if config is None:
        config = DEFAULT_CONFIG

    rng = random.Random(seed)

    schedule = pd.read_csv(schedule_path)
    schedule = schedule[schedule["week"] <= 18]
    schedule = schedule.sort_values(["season", "week"]).reset_index(drop=True)

    teams = sorted(set(schedule["home_team"]).union(schedule["away_team"]))

    team_elo = {t: INITIAL_ELO for t in teams}
    wins = {t: 0 for t in teams}
    losses = {t: 0 for t in teams}

    for _, game in schedule.iterrows():

        home = game["home_team"]
        away = game["away_team"]

        # Generate a simulated game outcome.
        actual = int(rng.random() < 0.5)

        result = run_game(
            home_elo=team_elo[home],
            away_elo=team_elo[away],
            context={
                "season": game["season"],
                "week": game["week"],
                "home_team": home,
                "away_team": away,
                "home_score": actual,
                "away_score": 1 - actual,
                "actual": actual,
            },
            config=config,
        )

        team_elo[home] = result["home_elo_post"]
        team_elo[away] = result["away_elo_post"]

        if actual == 1:
            wins[home] += 1
            losses[away] += 1
        else:
            wins[away] += 1
            losses[home] += 1

    standings = pd.DataFrame({
        "team": teams,
        "wins": [wins[t] for t in teams],
        "losses": [losses[t] for t in teams],
    }).sort_values(["wins", "losses", "team"], ascending=[False, True, True])

    elo_df = pd.DataFrame({
        "team": teams,
        "elo": [team_elo[t] for t in teams],
    }).sort_values("elo", ascending=False)

    return standings.reset_index(drop=True), elo_df.reset_index(drop=True)

# =========================
# MONTE CARLO SIMULATION
# =========================

def simulate_many_seasons(n_sims=500, schedule_path="data/nfl_games.csv", config=None, seed=42):
    """
    Runs repeated season simulations and returns simulated
    team win totals for every Monte Carlo iteration.
    """
    results = []

    for i in range(n_sims):

        standings, _ = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
        )

        for _, row in standings.iterrows():
            results.append({
                "sim_id": i,
                "team": row["team"],
                "wins": int(row["wins"]),
            })

    return pd.DataFrame(results)

# =========================
# SUMMARY STATISTICS
# =========================

def summarize_simulations(sim_results):
    """
    Computes summary statistics for simulated team win totals.
    """
    return sim_results.groupby("team")["wins"].agg(
        mean="mean",
        std="std",
        min="min",
        max="max",
        median="median",
    ).reset_index().sort_values("mean", ascending=False)

# =========================
# WIN DISTRIBUTIONS
# =========================

def win_distributions(sim_results):
    """
    Computes empirical win-total distributions from Monte Carlo
    simulation results.
    """
    dist = sim_results.groupby(["team", "wins"]).size().reset_index(name="count")
    dist["probability"] = dist.groupby("team")["count"].transform(lambda x: x / x.sum())

    return dist.sort_values(["team", "wins"])


if __name__ == "__main__":

    standings, elo_df = simulate_season()

    print(standings)
    print(elo_df)

    sim = simulate_many_seasons(n_sims=200)

    print(summarize_simulations(sim).head(10))