from pathlib import Path

import pandas as pd


BACKTEST_FILE = Path("outputs/backtest_MOV_HFA.csv")


def get_latest_elo_ratings():

    if not BACKTEST_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(BACKTEST_FILE)

    latest = (
        pd.concat(
            [
                df[["week", "home_team", "home_elo_post"]]
                .rename(
                    columns={
                        "home_team": "team",
                        "home_elo_post": "elo",
                    }
                ),

                df[["week", "away_team", "away_elo_post"]]
                .rename(
                    columns={
                        "away_team": "team",
                        "away_elo_post": "elo",
                    }
                ),
            ]
        )
        .sort_values("week")
        .groupby("team", as_index=False)
        .last()
        .sort_values(
            "elo",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    latest.insert(
        0,
        "Rank",
        range(
            1,
            len(latest) + 1,
        ),
    )

    return latest