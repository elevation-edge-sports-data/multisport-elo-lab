"""Lock-played-games: upcoming / in_progress / final fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from elo_lab.workflows.simulate_season import (
    describe_schedule_lock,
    format_lock_line,
    parse_locked_scores,
    simulate_season,
)


CONFIG = {"k": 20, "adjustments": {}}


def _upcoming_schedule() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "home_team": ["A", "B", "A"],
            "away_team": ["B", "C", "C"],
            "home_score": [pd.NA, pd.NA, pd.NA],
            "away_score": [pd.NA, pd.NA, pd.NA],
            "week": [1, 1, 2],
        }
    )


def _final_schedule() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "home_team": ["A", "B", "A"],
            "away_team": ["B", "C", "C"],
            "home_score": [24.0, 10.0, 31.0],
            "away_score": [10.0, 17.0, 14.0],
            "week": [1, 1, 2],
        }
    )


def _in_progress_schedule() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "home_team": ["A", "B", "A"],
            "away_team": ["B", "C", "C"],
            "home_score": [24.0, pd.NA, pd.NA],
            "away_score": [10.0, pd.NA, pd.NA],
            "week": [1, 1, 2],
        }
    )


def _wins(standings: pd.DataFrame) -> dict:
    return {row["team"]: int(row["wins"]) for _, row in standings.iterrows()}


def _elo(standings: pd.DataFrame) -> dict:
    return {row["team"]: float(row["elo"]) for _, row in standings.iterrows()}


def test_parse_locked_scores_skips_blank_and_ties():
    from elo_lab.workflows.simulate_season import parse_game_scores

    blank = pd.Series({"home_team": "A", "away_team": "B", "home_score": pd.NA, "away_score": pd.NA})
    tie = pd.Series({"home_team": "A", "away_team": "B", "home_score": 17, "away_score": 17})
    played = pd.Series({"home_team": "A", "away_team": "B", "home_score": 24, "away_score": 10})
    assert parse_locked_scores(blank) is None
    assert parse_locked_scores(tie) is None
    assert parse_locked_scores(played) == (24.0, 10.0)
    assert parse_game_scores(tie) == (17.0, 17.0)
    assert parse_game_scores(blank) is None


def test_describe_and_format_three_statuses():
    upcoming = describe_schedule_lock(_upcoming_schedule())
    live = describe_schedule_lock(_in_progress_schedule())
    final = describe_schedule_lock(_final_schedule())

    assert upcoming == {"n_games": 3, "n_locked": 0, "status": "upcoming"}
    assert live == {"n_games": 3, "n_locked": 1, "status": "in_progress"}
    assert final == {"n_games": 3, "n_locked": 3, "status": "final"}

    assert format_lock_line("NFL", "2026", upcoming) == "NFL 2026 · upcoming · 0/3 games locked"
    assert format_lock_line("NFL", "2026", live) == "NFL 2026 · in progress · 1/3 games locked"
    assert format_lock_line("NFL", "2026", final) == "NFL 2026 · 3/3 games locked"


def test_upcoming_is_sampled():
    schedule = _upcoming_schedule()
    s1, _, _ = simulate_season(schedule_df=schedule, config=CONFIG, seed=1, sport="NFL")
    s2, _, _ = simulate_season(schedule_df=schedule, config=CONFIG, seed=2, sport="NFL")
    assert _wins(s1) != _wins(s2) or _elo(s1) != _elo(s2)


def test_final_is_deterministic():
    schedule = _final_schedule()
    s1, e1, _ = simulate_season(schedule_df=schedule, config=CONFIG, seed=1, sport="NFL")
    s2, e2, _ = simulate_season(schedule_df=schedule, config=CONFIG, seed=99, sport="NFL")
    assert _wins(s1) == _wins(s2)
    assert _wins(s1) == {"A": 2, "B": 0, "C": 1}
    for team in ("A", "B", "C"):
        assert abs(e1[team] - e2[team]) < 1e-9
        assert abs(_elo(s1)[team] - _elo(s2)[team]) < 1e-9


def test_in_progress_locks_prefix_and_samples_rest():
    schedule = _in_progress_schedule()
    runs = [
        simulate_season(schedule_df=schedule, config=CONFIG, seed=seed, sport="NFL")
        for seed in (1, 2, 3, 4, 5)
    ]
    win_maps = [_wins(standings) for standings, _, _ in runs]

    for wins in win_maps:
        assert wins["A"] >= 1
        assert wins["B"] <= 1

    assert len({tuple(sorted(w.items())) for w in win_maps}) > 1


def test_tie_is_locked_not_sampled():
    schedule = pd.DataFrame(
        {
            "home_team": ["A"],
            "away_team": ["B"],
            "home_score": [20.0],
            "away_score": [20.0],
            "week": [1],
        }
    )
    info = describe_schedule_lock(schedule)
    assert info == {"n_games": 1, "n_locked": 1, "status": "final"}
    s1, e1, _ = simulate_season(schedule_df=schedule, config=CONFIG, seed=1, sport="NFL")
    s2, e2, _ = simulate_season(schedule_df=schedule, config=CONFIG, seed=99, sport="NFL")
    assert _wins(s1) == {"A": 0, "B": 0}
    assert _wins(s2) == {"A": 0, "B": 0}
    assert e1["A"] == e2["A"] == 1500.0
    assert e1["B"] == e2["B"] == 1500.0
