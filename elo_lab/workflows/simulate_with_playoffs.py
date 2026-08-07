"""
elo_lab/workflows/simulate_with_playoffs.py

Drop-in wrapper that runs the existing season simulation and then the
sport-specific playoffs (NFL / NHL / NBA).
Keeps the original simulate_season.py completely untouched.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Optional, Tuple

import pandas as pd

from elo_lab.workflows.simulate_season import (
    simulate_many_seasons as _original_simulate_many_seasons,
    simulate_season,
)


# ---------------------------------------------------------------------------
# Round names per sport (used for probability counters)
# ---------------------------------------------------------------------------
PLAYOFF_ROUNDS = {
    "NFL": ["Wild Card", "Divisional", "Conference", "Super Bowl", "Champion"],
    "NHL": [
        "First Round",
        "Second Round",
        "Conference Finals",
        "Stanley Cup Final",
        "Champion",
    ],
    "NBA": [
        "Play-In",
        "First Round",
        "Conference Semifinals",
        "Conference Finals",
        "NBA Finals",
        "Champion",
    ],
}


def _get_playoff_runner(sport: str):
    """Return the correct run_playoffs_after_season for the given sport."""
    sport = sport.upper()
    if sport == "NFL":
        from elo_lab.playoffs.nfl import run_playoffs_after_season
        return run_playoffs_after_season
    if sport == "NHL":
        from elo_lab.playoffs.nhl import run_playoffs_after_season
        return run_playoffs_after_season
    if sport == "NBA":
        from elo_lab.playoffs.nba import run_playoffs_after_season
        return run_playoffs_after_season
    return None


def simulate_many_seasons(
    n_sims: int = 500,
    schedule_path: Optional[str] = None,
    config: Optional[dict] = None,
    seed: int = 42,
    initial_ratings: Optional[dict] = None,
    sport: str = "NFL",
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]], pd.DataFrame]:
    """
    Same interface as the original simulate_many_seasons, but also returns
    playoff probabilities when a playoff module exists for the sport.

    Returns
    -------
    results_df : pd.DataFrame
        Regular-season results (sim_id, team, wins, points).
    playoff_probs : dict
        {
          team: {
            "<round_name>": p,
            ...
            "Champion": p,
          }
        }
        Empty dict for unsupported sports.
    elo_evolution : pd.DataFrame
        Aggregated Elo trajectories from the same regular-season sims
        (team, games_played, mean_elo, p05_elo, p95_elo).
    """
    # 1. Regular-season Monte Carlo — standings + Elo from the SAME outcomes
    results_df, elo_evolution = _original_simulate_many_seasons(
        n_sims=n_sims,
        schedule_path=schedule_path,
        config=config,
        seed=seed,
        initial_ratings=initial_ratings,
        sport=sport,
        return_elo_evolution=True,
    )

    playoff_probs: Dict[str, Dict[str, float]] = {}
    run_playoffs = _get_playoff_runner(sport)

    if run_playoffs is None:
        return results_df, playoff_probs, elo_evolution

    # 2. Re-simulate a capped number of full seasons so we have complete
    #    standings + Elo for seeding / bracket construction.
    counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rounds = PLAYOFF_ROUNDS.get(sport.upper(), [])
    n_playoff_sims = min(n_sims, 300)

    for i in range(n_playoff_sims):
        standings, team_elo, _ = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
            initial_ratings=initial_ratings,
            sport=sport,
        )

        result = run_playoffs(
            standings_df=standings,
            team_elo=team_elo,
            home_advantage=55.0,  # later: pull from sport config
        )

        for team, reached in result.team_reached.items():
            for rnd in rounds:
                if reached.get(rnd, False):
                    counters[team][rnd] += 1

    playoff_probs = {
        team: {rnd: counters[team][rnd] / n_playoff_sims for rnd in rounds}
        for team in counters
    }

    return results_df, playoff_probs, elo_evolution
