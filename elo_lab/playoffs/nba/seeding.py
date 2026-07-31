"""
NBA playoff qualification, Play-In setup, and fixed-bracket seeding.

Rules (current format):
- Top 6 teams in each conference automatically qualify (seeds 1–6).
- Seeds 7–10 enter the Play-In Tournament:
    • 7 vs 8  → winner becomes #7 seed, loser gets second chance
    • 9 vs 10 → winner advances, loser is eliminated
    • Loser of 7/8 hosts winner of 9/10 → winner becomes #8 seed
- After Play-In the bracket is the classic fixed 1–8:
    1v8, 2v7, 3v6, 4v5  (no reseeding)
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from .models import TeamStanding


def better_record(
    a: TeamStanding,
    b: TeamStanding,
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> bool:
    """Return True if team a ranks higher than team b (win_pct primary)."""
    if a.win_pct != b.win_pct:
        return a.win_pct > b.win_pct
    if a.wins != b.wins:
        return a.wins > b.wins

    if tiebreaker_fn is not None:
        return tiebreaker_fn(a, b) > 0

    return a.team_id < b.team_id


def apply_tiebreakers(
    teams: List[TeamStanding],
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> List[TeamStanding]:
    """Sort teams by win percentage / wins."""
    if not teams:
        return []

    def sort_key(t: TeamStanding):
        return (-t.win_pct, -t.wins, t.team_id)

    sorted_teams = sorted(teams, key=sort_key)

    if tiebreaker_fn is not None:
        for i in range(len(sorted_teams) - 1):
            a, b = sorted_teams[i], sorted_teams[i + 1]
            if a.win_pct == b.win_pct and a.wins == b.wins:
                if tiebreaker_fn(a, b) < 0:
                    sorted_teams[i], sorted_teams[i + 1] = b, a

    return sorted_teams


def seed_nba_playoffs(
    standings: List[TeamStanding],
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> Dict[str, Dict]:
    """
    Produce the Play-In participants and the eventual 1–8 seeds structure
    for each conference.

    Returns
    -------
    dict
        {
          "Eastern": {
              "auto": [seed1_id … seed6_id],          # already locked
              "play_in": [seed7_id, seed8_id, seed9_id, seed10_id],
              "seeds": {team_id: int}                 # provisional 1-10
          },
          "Western": { ... }
        }
    """
    by_conf: Dict[str, List[TeamStanding]] = {"Eastern": [], "Western": []}
    for s in standings:
        if s.conference in by_conf:
            by_conf[s.conference].append(s)

    result: Dict[str, Dict] = {}

    for conf, teams in by_conf.items():
        if not teams:
            result[conf] = {"auto": [], "play_in": [], "seeds": {}}
            continue

        ranked = apply_tiebreakers(teams, tiebreaker_fn)

        auto = [t.team_id for t in ranked[:6]]
        play_in = [t.team_id for t in ranked[6:10]]

        seeds = {t.team_id: i + 1 for i, t in enumerate(ranked[:10])}

        result[conf] = {
            "auto": auto,
            "play_in": play_in,
            "seeds": seeds,
        }

    return result
