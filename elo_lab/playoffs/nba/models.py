"""
NBA Playoff data structures for Multisport Elo Lab.

Parallel to elo_lab.playoffs.nfl.models and nhl.models so aggregation /
dashboard code can work across sports with minimal changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TeamStanding:
    """Final regular-season standing for one team."""
    team_id: str
    conference: str          # "Eastern" | "Western"
    division: str            # Atlantic / Central / Southeast / Northwest / Pacific / Southwest
    wins: float
    losses: float
    win_pct: float
    elo: float = 1500.0

    # Optional fields
    points_for: Optional[int] = None
    points_against: Optional[int] = None


@dataclass
class GameResult:
    """Result of a single playoff (or play-in) game."""
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
    """Results of one playoff round within a conference (or NBA Finals)."""
    name: str                # "Play-In", "First Round", "Conference Semifinals",
                             # "Conference Finals", "NBA Finals"
    series: List[SeriesResult] = field(default_factory=list)
    games: List[GameResult] = field(default_factory=list)  # used for single-game Play-In
    advancers: List[str] = field(default_factory=list)


@dataclass
class PlayoffResult:
    """Complete playoff outcome for one Monte Carlo season."""
    conference_results: Dict[str, List[RoundResult]]  # "Eastern" / "Western" → list of rounds
    nba_finals: Optional[SeriesResult] = None
    champion: Optional[str] = None

    # team_id → {round_name: bool}
    team_reached: Dict[str, Dict[str, bool]] = field(default_factory=dict)
