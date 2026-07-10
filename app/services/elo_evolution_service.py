from pathlib import Path

import pandas as pd


BACKTEST_FILE = Path("outputs/backtest_MOV_HFA.csv")


def get_elo_evolution():

    if not BACKTEST_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(BACKTEST_FILE)

    home = (
        df[
            [
                "season",
                "week",
                "home_team",
                "home_elo_post",
            ]
        ]
        .rename(
            columns={
                "home_team": "team",
                "home_elo_post": "elo",
            }
        )
    )

    away = (
        df[
            [
                "season",
                "week",
                "away_team",
                "away_elo_post",
            ]
        ]
        .rename(
            columns={
                "away_team": "team",
                "away_elo_post": "elo",
            }
        )
    )

    evolution = pd.concat(
        [
            home,
            away,
        ],
        ignore_index=True,
    )

    evolution["week_index"] = (
        evolution["season"] * 100
        + evolution["week"]
    )

    evolution = (
        evolution
        .sort_values(
            [
                "team",
                "week_index",
            ]
        )
        .reset_index(drop=True)
    )

    # Display only week number on x-axis
    evolution["week_label"] = (
        "W"
        + evolution["week"].astype(str)
    )

    # Force Plotly to respect chronological ordering
    ordered_labels = (
        evolution
        .sort_values("week_index")["week_label"]
        .drop_duplicates()
        .tolist()
    )

    evolution["week_label"] = pd.Categorical(
        evolution["week_label"],
        categories=ordered_labels,
        ordered=True,
    )

    return evolution