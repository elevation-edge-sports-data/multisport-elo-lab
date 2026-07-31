"""
Example integration with a Monte Carlo season simulation loop.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List

from .models import PlayoffResult, TeamStanding
from .simulation import run_nhl_playoff_from_standings


def accumulate_playoff_probabilities(
    all_standings: List[List[TeamStanding]],
    n_sims: int,
    home_advantage: float = 55.0,
    base_seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """
    Run playoff simulation for every completed regular-season outcome
    and return empirical probabilities.

    Returns
    -------
    dict
        {
          team_id: {
            "First Round": p,
            "Second Round": p,
            "Conference Finals": p,
            "Stanley Cup Final": p,
            "Champion": p,
          },
          ...
        }
    """
    counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rounds = [
        "First Round",
        "Second Round",
        "Conference Finals",
        "Stanley Cup Final",
        "Champion",
    ]

    for i, standings in enumerate(all_standings):
        rng = random.Random(base_seed + i)
        result: PlayoffResult = run_nhl_playoff_from_standings(
            standings=standings,
            home_advantage=home_advantage,
            rng=rng,
        )

        for team, reached in result.team_reached.items():
            for rnd in rounds:
                if reached.get(rnd, False):
                    counters[team][rnd] += 1

    probs: Dict[str, Dict[str, float]] = {}
    for team, counts in counters.items():
        probs[team] = {rnd: counts.get(rnd, 0) / n_sims for rnd in rounds}

    return probs
