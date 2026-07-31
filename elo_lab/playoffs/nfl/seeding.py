"""
NFL playoff qualification and seeding.

Implements the accepted rules:
- 4 division winners + 3 wild cards per conference
- Seeds 1-4 = division winners ordered by record
- Seeds 5-7 = wild cards ordered by record
- Tiebreakers applied only when records are identical
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from .models import TeamStanding


def better_record(
    a: TeamStanding,
    b: TeamStanding,
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> bool:
    """
    Return True if team a has a better record than team b.
    Primary key is win_pct, then wins. Falls back to tiebreaker_fn if equal.
    """
    if a.win_pct != b.win_pct:
        return a.win_pct > b.win_pct
    if a.wins != b.wins:
        return a.wins > b.wins

    if tiebreaker_fn is not None:
        return tiebreaker_fn(a, b) > 0

    # Final deterministic fallback (stable sort by team_id)
    return a.team_id < b.team_id


def apply_tiebreakers(
    teams: List[TeamStanding],
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> List[TeamStanding]:
    """
    Sort teams by record, applying the provided tiebreaker when necessary.
    The tiebreaker_fn should return >0 if first arg ranks higher, <0 otherwise.
    """
    if not teams:
        return []

    # Python's sort is stable; we use a key that encodes the primary metrics
    # and falls back to the external tiebreaker only on true ties.
    def sort_key(t: TeamStanding):
        # Higher is better for win_pct and wins
        return (-t.win_pct, -t.wins, t.team_id)

    sorted_teams = sorted(teams, key=sort_key)

    # If a custom multi-team or pairwise tiebreaker is supplied and
    # we detect true ties, we can refine further. For the MVP we keep
    # the primary sort and let the caller inject a more complete
    # NFL tiebreaker procedure later.
    if tiebreaker_fn is not None:
        # Simple pairwise refinement for adjacent ties (good enough for MVP)
        for i in range(len(sorted_teams) - 1):
            a, b = sorted_teams[i], sorted_teams[i + 1]
            if a.win_pct == b.win_pct and a.wins == b.wins:
                if tiebreaker_fn(a, b) < 0:
                    sorted_teams[i], sorted_teams[i + 1] = b, a

    return sorted_teams


def seed_nfl_playoffs(
    standings: List[TeamStanding],
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> Dict[str, List[str]]:
    """
    Produce the 7 playoff seeds for each conference.

    Returns
    -------
    dict
        {"AFC": [seed1_id, seed2_id, ..., seed7_id],
         "NFC": [seed1_id, seed2_id, ..., seed7_id]}
    """
    by_conf: Dict[str, List[TeamStanding]] = {"AFC": [], "NFC": []}
    for s in standings:
        if s.conference in by_conf:
            by_conf[s.conference].append(s)

    seeded: Dict[str, List[str]] = {}

    for conf, teams in by_conf.items():
        if not teams:
            seeded[conf] = []
            continue

        # --- Division winners ---
        div_winners: Dict[str, TeamStanding] = {}
        for t in teams:
            current = div_winners.get(t.division)
            if current is None or better_record(t, current, tiebreaker_fn):
                div_winners[t.division] = t

        div_winner_list = apply_tiebreakers(list(div_winners.values()), tiebreaker_fn)

        # --- Wild cards = remaining teams ---
        winner_ids = {t.team_id for t in div_winner_list}
        remaining = [t for t in teams if t.team_id not in winner_ids]
        remaining = apply_tiebreakers(remaining, tiebreaker_fn)

        seeds = [t.team_id for t in div_winner_list] + [t.team_id for t in remaining[:3]]
        seeded[conf] = seeds

    return seeded
