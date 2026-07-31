"""
Example integration with a Monte Carlo season simulation loop.

This file shows the minimal glue required to accumulate playoff
probabilities across many regular-season simulations.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List

from .models import PlayoffResult, TeamStanding
from .simulation import run_nfl_playoff_from_standings


def accumulate_playoff_probabilities(
    all_standings: List[List[TeamStanding]],
    n_sims: int,
    home_advantage: float = 55.0,
    base_seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """
    Run playoff simulation for every completed regular-season outcome
    and return empirical probabilities.

    Parameters
    ----------
    all_standings
        List of length n_sims; each element is the List[TeamStanding]
        produced by one regular-season Monte Carlo draw.
    n_sims
        Number of Monte Carlo seasons (should equal len(all_standings)).
    home_advantage
        Elo home-field value used in playoff games.
    base_seed
        Base RNG seed for reproducibility.

    Returns
    -------
    dict
        {
          team_id: {
            "Wild Card": p,
            "Divisional": p,
            "Conference": p,
            "Super Bowl": p,
            "Champion": p,
          },
          ...
        }
    """
    counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rounds = ["Wild Card", "Divisional", "Conference", "Super Bowl", "Champion"]

    for i, standings in enumerate(all_standings):
        rng = random.Random(base_seed + i)
        result: PlayoffResult = run_nfl_playoff_from_standings(
            standings=standings,
            home_advantage=home_advantage,
            rng=rng,
        )

        # Count round reach
        for team, reached in result.team_reached.items():
            for rnd in rounds:
                if reached.get(rnd, False):
                    counters[team][rnd] += 1

        # Champion is already counted via team_reached – no extra increment

    # Convert counts → probabilities
    probs: Dict[str, Dict[str, float]] = {}
    for team, counts in counters.items():
        probs[team] = {rnd: counts.get(rnd, 0) / n_sims for rnd in rounds}

    return probs


# ----------------------------------------------------------------------
# Minimal usage sketch (pseudo-code that would live inside the main
# Multisport Elo Lab season-simulation service)
# ----------------------------------------------------------------------
#
# from nfl_playoffs.integration import accumulate_playoff_probabilities
#
# # After the regular-season Monte Carlo loop has finished:
# #   all_standings = [extract_standings(season_i) for season_i in monte_carlo_results]
#
# playoff_probs = accumulate_playoff_probabilities(
#     all_standings=all_standings,
#     n_sims=len(all_standings),
#     home_advantage=config.home_advantage_nfl,
# )
#
# # Then surface playoff_probs in the Streamlit dashboard
# # (new columns or a dedicated "Playoff Outlook" section).
