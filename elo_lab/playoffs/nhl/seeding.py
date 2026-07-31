"""
NHL playoff qualification and fixed-bracket seeding.

Rules (current format):
- Top 3 teams in each division automatically qualify.
- Next 2 highest point totals in each conference become wild cards
  (regardless of division).
- Bracket is fixed (no reseeding between rounds):

  Within each conference the four series are:
    1. Division winner with best record vs lower wild card
    2. Other division winner vs higher wild card
    3. 2nd-place vs 3rd-place in Division A
    4. 2nd-place vs 3rd-place in Division B

Home-ice advantage in the first two rounds goes to the higher seed /
better regular-season record.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from .models import TeamStanding


def better_record(
    a: TeamStanding,
    b: TeamStanding,
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> bool:
    """
    Return True if team a ranks higher than team b.
    Primary key is points, then regulation wins (if available), then win_pct.
    """
    if a.points != b.points:
        return a.points > b.points

    # Prefer regulation wins when present (official NHL tiebreaker)
    a_rw = a.regulation_wins if a.regulation_wins is not None else a.wins
    b_rw = b.regulation_wins if b.regulation_wins is not None else b.wins
    if a_rw != b_rw:
        return a_rw > b_rw

    if a.win_pct != b.win_pct:
        return a.win_pct > b.win_pct

    if tiebreaker_fn is not None:
        return tiebreaker_fn(a, b) > 0

    # Deterministic fallback
    return a.team_id < b.team_id


def apply_tiebreakers(
    teams: List[TeamStanding],
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> List[TeamStanding]:
    """Sort teams by the NHL ranking criteria."""
    if not teams:
        return []

    def sort_key(t: TeamStanding):
        rw = t.regulation_wins if t.regulation_wins is not None else t.wins
        return (-t.points, -rw, -t.win_pct, t.team_id)

    sorted_teams = sorted(teams, key=sort_key)

    if tiebreaker_fn is not None:
        for i in range(len(sorted_teams) - 1):
            a, b = sorted_teams[i], sorted_teams[i + 1]
            if (a.points == b.points and
                    (a.regulation_wins or a.wins) == (b.regulation_wins or b.wins)):
                if tiebreaker_fn(a, b) < 0:
                    sorted_teams[i], sorted_teams[i + 1] = b, a

    return sorted_teams


def seed_nhl_playoffs(
    standings: List[TeamStanding],
    tiebreaker_fn: Optional[Callable[[TeamStanding, TeamStanding], int]] = None,
) -> Dict[str, Dict]:
    """
    Produce the fixed-bracket seeds for each conference.

    Returns
    -------
    dict
        {
          "Eastern": {
              "series": [
                  {"higher": team_id, "lower": team_id, "label": "..."},
                  ...
              ],
              "seeds": {team_id: seed_number, ...}   # 1-8 for reference
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
            result[conf] = {"series": [], "seeds": {}}
            continue

        # Group by division
        by_div: Dict[str, List[TeamStanding]] = {}
        for t in teams:
            by_div.setdefault(t.division, []).append(t)

        # Sort each division
        div_sorted: Dict[str, List[TeamStanding]] = {
            div: apply_tiebreakers(lst, tiebreaker_fn)
            for div, lst in by_div.items()
        }

        # Top-3 automatic qualifiers per division
        auto: List[TeamStanding] = []
        for div_teams in div_sorted.values():
            auto.extend(div_teams[:3])

        auto_ids = {t.team_id for t in auto}

        # Wild cards = next two highest points in the conference
        remaining = [t for t in teams if t.team_id not in auto_ids]
        remaining = apply_tiebreakers(remaining, tiebreaker_fn)
        wild_cards = remaining[:2]

        # Division winners (1st in each division), ordered by points
        div_winners = []
        for div_teams in div_sorted.values():
            if div_teams:
                div_winners.append(div_teams[0])
        div_winners = apply_tiebreakers(div_winners, tiebreaker_fn)

        # Assign the four series (fixed bracket)
        # Series 1: best division winner vs lower wild card
        # Series 2: other division winner vs higher wild card
        # Series 3 & 4: 2nd vs 3rd inside each division

        series: List[Dict] = []
        seeds: Dict[str, int] = {}

        if len(div_winners) >= 2 and len(wild_cards) >= 2:
            # Higher / lower wild card by ranking
            wc_sorted = apply_tiebreakers(wild_cards, tiebreaker_fn)
            higher_wc = wc_sorted[0]
            lower_wc = wc_sorted[1]

            best_div_winner = div_winners[0]
            other_div_winner = div_winners[1]

            series.append({
                "higher": best_div_winner.team_id,
                "lower": lower_wc.team_id,
                "label": f"{best_div_winner.division} #1 vs WC2",
            })
            series.append({
                "higher": other_div_winner.team_id,
                "lower": higher_wc.team_id,
                "label": f"{other_div_winner.division} #1 vs WC1",
            })

            # 2 vs 3 inside each division
            for div, div_teams in div_sorted.items():
                if len(div_teams) >= 3:
                    series.append({
                        "higher": div_teams[1].team_id,
                        "lower": div_teams[2].team_id,
                        "label": f"{div} #2 vs #3",
                    })

            # Assign seed numbers 1-8 for reference / home-ice
            # 1 = best division winner, 2 = other division winner,
            # 3-6 = the four 2nd/3rd place teams ordered by points,
            # 7 = higher WC, 8 = lower WC
            ordered = (
                [best_div_winner, other_div_winner]
                + apply_tiebreakers(
                    [t for t in auto if t.team_id not in {best_div_winner.team_id, other_div_winner.team_id}],
                    tiebreaker_fn,
                )
                + [higher_wc, lower_wc]
            )
            for i, t in enumerate(ordered):
                seeds[t.team_id] = i + 1

        result[conf] = {"series": series, "seeds": seeds}

    return result
