"""
NFL Playoff data structures for Multisport Elo Lab.

These dataclasses are deliberately minimal and match the MVP specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TeamStanding:
    """Final regular-season standing for one team."""
    team_id: str
    conference: str          # "AFC" | "NFC"
    division: str            # e.g. "AFC East", "NFC West"
    wins: float              # ties count as 0.5
    losses: float
    win_pct: float
    elo: float = 1500.0

    # Optional fields – only populated if the upstream season simulation
    # already produces them. Used by tiebreakers when available.
    points_for: Optional[int] = None
    points_against: Optional[int] = None
    # Add more optional cumulative stats here later if richer data arrives
    # (e.g. division_wins, conference_wins, head_to_head matrix, etc.)


@dataclass
class GameResult:
    """Result of a single playoff game."""
    home: str
    away: str
    winner: str
    home_win_prob: float


@dataclass
class RoundResult:
    """Results of one playoff round within a conference (or Super Bowl)."""
    name: str                # "Wild Card", "Divisional", "Conference", "Super Bowl"
    games: List[GameResult] = field(default_factory=list)
    advancers: List[str] = field(default_factory=list)  # team_ids that advance


@dataclass
class PlayoffResult:
    """Complete playoff outcome for one Monte Carlo season."""
    conference_results: Dict[str, List[RoundResult]]  # "AFC" / "NFC" → list of rounds
    super_bowl: Optional[GameResult] = None
    champion: Optional[str] = None

    # Convenience structure for probability aggregation across many seasons.
    # team_id → {round_name: bool}
    team_reached: Dict[str, Dict[str, bool]] = field(default_factory=dict)
