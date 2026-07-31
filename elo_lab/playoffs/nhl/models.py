"""
NHL Playoff data structures for Multisport Elo Lab.

Deliberately parallel to elo_lab.playoffs.nfl.models so the same
aggregation / dashboard code can work across sports with minimal changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TeamStanding:
    """Final regular-season standing for one team."""
    team_id: str
    conference: str          # "Eastern" | "Western"
    division: str            # "Atlantic" | "Metropolitan" | "Central" | "Pacific"
    wins: float              # regulation + OT wins (for reference)
    losses: float
    points: float            # primary ranking metric in NHL
    win_pct: float           # points / max_possible (or wins-based fallback)
    elo: float = 1500.0

    # Optional fields – populated when upstream data is available
    points_for: Optional[int] = None
    points_against: Optional[int] = None
    regulation_wins: Optional[int] = None  # useful for NHL tiebreakers


@dataclass
class GameResult:
    """Result of a single playoff game."""
    home: str
    away: str
    winner: str
    home_win_prob: float


@dataclass
class SeriesResult:
    """Result of a best-of-7 series."""
    higher_seed: str
    lower_seed: str
    winner: str
    games: List[GameResult] = field(default_factory=list)
    higher_seed_wins: int = 0
    lower_seed_wins: int = 0


@dataclass
class RoundResult:
    """Results of one playoff round within a conference (or Stanley Cup Final)."""
    name: str                # "First Round", "Second Round", "Conference Finals", "Stanley Cup Final"
    series: List[SeriesResult] = field(default_factory=list)
    advancers: List[str] = field(default_factory=list)


@dataclass
class PlayoffResult:
    """Complete playoff outcome for one Monte Carlo season."""
    conference_results: Dict[str, List[RoundResult]]  # "Eastern" / "Western" → list of rounds
    stanley_cup_final: Optional[SeriesResult] = None
    champion: Optional[str] = None

    # Convenience structure for probability aggregation across many seasons.
    # team_id → {round_name: bool}
    team_reached: Dict[str, Dict[str, bool]] = field(default_factory=dict)
