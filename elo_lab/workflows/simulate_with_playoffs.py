"""
elo_lab/workflows/simulate_with_playoffs.py

Drop-in wrapper that runs the existing season simulation and then the NFL playoffs.
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
from elo_lab.playoffs.nfl import run_playoffs_after_season


def simulate_many_seasons(
    n_sims: int = 500,
    schedule_path: Optional[str] = None,
    config: Optional[dict] = None,
    seed: int = 42,
    initial_ratings: Optional[dict] = None,
    sport: str = "NFL",
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    """
    Same interface as the original simulate_many_seasons, but also returns
    playoff probabilities when sport == "NFL".

    Returns
    -------
    results_df : pd.DataFrame
        Identical to the original thin results (sim_id, team, wins, points).
    playoff_probs : dict
        {
          team: {
            "Wild Card": p,
            "Divisional": p,
            "Conference": p,
            "Super Bowl": p,
            "Champion": p,
          }
        }
        Empty dict for non-NFL sports.
    """
    # 1. Run the original regular-season Monte Carlo (unchanged)
    results_df = _original_simulate_many_seasons(
        n_sims=n_sims,
        schedule_path=schedule_path,
        config=config,
        seed=seed,
        initial_ratings=initial_ratings,
        sport=sport,
    )

    playoff_probs: Dict[str, Dict[str, float]] = {}

    if sport != "NFL":
        return results_df, playoff_probs

    # 2. Run full season + playoff simulations to obtain proper probabilities.
    #    We re-simulate a capped number of full seasons so we still have
    #    access to the complete standings + Elo (the thin results_df alone
    #    is not enough for seeding).
    counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rounds = ["Wild Card", "Divisional", "Conference", "Super Bowl", "Champion"]

    # Cap for responsiveness; raise this number if you want tighter estimates
    n_playoff_sims = min(n_sims, 300)

    for i in range(n_playoff_sims):
        standings, team_elo, _ = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
            initial_ratings=initial_ratings,
            sport=sport,
        )

        result = run_playoffs_after_season(
            standings_df=standings,
            team_elo=team_elo,
            home_advantage=55.0,  # later: pull from sport config
        )

        for team, reached in result.team_reached.items():
            for rnd in rounds:
                if reached.get(rnd, False):
                    counters[team][rnd] += 1
        # Note: Champion is already marked inside team_reached; do not double-count.

    playoff_probs = {
        team: {rnd: counters[team][rnd] / n_playoff_sims for rnd in rounds}
        for team in counters
    }

    return results_df, playoff_probs
