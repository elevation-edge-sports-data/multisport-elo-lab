"""
Example integration with a Monte Carlo season simulation loop.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List

from .models import PlayoffResult, TeamStanding
from .simulation import run_nba_playoff_from_standings


def accumulate_playoff_probabilities(
    all_standings: List[List[TeamStanding]],
    n_sims: int,
    home_advantage: float = 55.0,
    base_seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """
    Run playoff simulation for every completed regular-season outcome
    and return empirical probabilities.
    """
    counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rounds = [
        "Play-In",
        "First Round",
        "Conference Semifinals",
        "Conference Finals",
        "NBA Finals",
        "Champion",
    ]

    for i, standings in enumerate(all_standings):
        rng = random.Random(base_seed + i)
        result: PlayoffResult = run_nba_playoff_from_standings(
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
