"""
Season simulation workflow.

Simulates complete seasons using the Elo engine,
supports repeated Monte Carlo simulations, and summarizes
simulated season outcomes.
"""

import random
import pandas as pd

from elo_lab.engine.game_runner import run_game
from elo_lab.engine.pregame import compute_pregame
from elo_lab.engine.constants import INITIAL_ELO


DEFAULT_CONFIG = {
    "k": 20,
    "adjustments": {
        "home_field": {
            "enabled": True,
            "value": 55,
        },
        "margin_of_victory": {
            "enabled": False,
        },
    },
}


# ==========================================================
# SINGLE SEASON SIMULATION
# ==========================================================

def _simulate_season_internal(
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
    initial_ratings=None,
    track_history=False,
):

    if config is None:
        config = DEFAULT_CONFIG

    rng = random.Random(seed)

    schedule = pd.read_csv(schedule_path)

    schedule = schedule[
        schedule["week"] <= 18
    ]

    schedule = schedule.sort_values(
        [
            "season",
            "week",
        ]
    ).reset_index(drop=True)

    teams = sorted(
        set(schedule["home_team"]).union(
            schedule["away_team"]
        )
    )

    if initial_ratings is None:

        team_elo = {
            team: INITIAL_ELO
            for team in teams
        }

    else:

        team_elo = {
            team: initial_ratings.get(
                team,
                INITIAL_ELO,
            )
            for team in teams
        }


    wins = {
        team: 0
        for team in teams
    }

    losses = {
        team: 0
        for team in teams
    }

    elo_history = []


    for _, game in schedule.iterrows():

        home = game["home_team"]
        away = game["away_team"]


        pregame = compute_pregame(
            home_elo=team_elo[home],
            away_elo=team_elo[away],
            context={
                "season": game["season"],
                "week": game["week"],
                "home_team": home,
                "away_team": away,
            },
            config=config,
        )


        actual = int(
            rng.random()
            <
            pregame["p_home"]
        )


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


        team_elo[home] = result[
            "home_elo_post"
        ]

        team_elo[away] = result[
            "away_elo_post"
        ]


        if actual == 1:
            wins[home] += 1
            losses[away] += 1
        else:
            wins[away] += 1
            losses[home] += 1


        if track_history:

            for team in teams:

                elo_history.append(
                    {
                        "week": int(game["week"]),
                        "team": team,
                        "elo": team_elo[team],
                    }
                )


    standings = pd.DataFrame(
        {
            "team": teams,
            "wins": [
                wins[t]
                for t in teams
            ],
            "losses": [
                losses[t]
                for t in teams
            ],
        }
    ).sort_values(
        [
            "wins",
            "losses",
            "team",
        ],
        ascending=[
            False,
            True,
            True,
        ],
    )


    elo_df = pd.DataFrame(
        {
            "team": teams,
            "elo": [
                team_elo[t]
                for t in teams
            ],
        }
    ).sort_values(
        "elo",
        ascending=False,
    )


    elo_history_df = pd.DataFrame(
        elo_history
    )


    return (
        standings.reset_index(drop=True),
        elo_df.reset_index(drop=True),
        elo_history_df.reset_index(drop=True),
    )


def simulate_season(
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
    initial_ratings=None,
):

    standings, elo_df, _ = _simulate_season_internal(
        schedule_path=schedule_path,
        config=config,
        seed=seed,
        initial_ratings=initial_ratings,
        track_history=False,
    )

    return (
        standings,
        elo_df,
    )


def simulate_season_with_history(
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
    initial_ratings=None,
):

    return _simulate_season_internal(
        schedule_path=schedule_path,
        config=config,
        seed=seed,
        initial_ratings=initial_ratings,
        track_history=True,
    )


# ==========================================================
# MONTE CARLO SIMULATION
# ==========================================================

def simulate_many_seasons(
    n_sims=500,
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
    initial_ratings=None,
):

    results = []


    for i in range(n_sims):

        standings, _ = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
            initial_ratings=initial_ratings,
        )


        for _, row in standings.iterrows():

            results.append(
                {
                    "sim_id": i,
                    "team": row["team"],
                    "wins": int(row["wins"]),
                }
            )


    return pd.DataFrame(results)


def simulate_elo_evolution(
    n_sims=500,
    schedule_path="data/nfl_games.csv",
    config=None,
    seed=42,
    initial_ratings=None,
):

    history = []


    for i in range(n_sims):

        _, _, elo_history = simulate_season_with_history(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
            initial_ratings=initial_ratings,
        )

        elo_history["sim_id"] = i

        history.append(
            elo_history
        )


    history = pd.concat(
        history,
        ignore_index=True,
    )


    evolution = (
        history
        .groupby(
            [
                "sim_id",
                "team",
                "week",
            ]
        )["elo"]
        .last()
        .reset_index()
        .groupby(
            [
                "team",
                "week",
            ]
        )["elo"]
        .agg(
            mean_elo="mean",
            p05_elo=lambda x: x.quantile(0.05),
            p95_elo=lambda x: x.quantile(0.95),
        )
        .reset_index()
        .sort_values(
            [
                "team",
                "week",
            ]
        )
    )


    return evolution


# ==========================================================
# SUMMARY STATISTICS
# ==========================================================

def summarize_simulations(sim_results):

    return (
        sim_results
        .groupby("team")["wins"]
        .agg(
            mean="mean",
            std="std",
            min="min",
            max="max",
            median="median",
        )
        .reset_index()
        .sort_values(
            "mean",
            ascending=False,
        )
    )


# ==========================================================
# WIN DISTRIBUTIONS
# ==========================================================

def win_distributions(sim_results):

    dist = (
        sim_results
        .groupby(
            [
                "team",
                "wins",
            ]
        )
        .size()
        .reset_index(
            name="count"
        )
    )


    dist["probability"] = (
        dist.groupby("team")["count"]
        .transform(
            lambda x: x / x.sum()
        )
    )


    return dist.sort_values(
        [
            "team",
            "wins",
        ]
    )


if __name__ == "__main__":

    standings, elo_df = simulate_season()

    print(standings)
    print(elo_df)

    sim = simulate_many_seasons(
        n_sims=200
    )

    print(
        summarize_simulations(sim)
        .head(10)
    )