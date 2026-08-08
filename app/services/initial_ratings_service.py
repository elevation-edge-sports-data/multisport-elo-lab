"""
Initial Elo ratings service (multiseason-aware).

Supports:
  rating_source   : "playoffs" | "regular_season"   (default "playoffs")
  rating_basis    : "record"   | "elo"              (default "record")
  apply_regression: bool                            (default False)

Always guarantees every team in the schedule has an entry
(prevents KeyError inside simulate_season).
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

try:
    from metadata import NHL_TEAMS, NFL_TEAMS, NBA_TEAMS
except ImportError:
    try:
        from app.metadata import NHL_TEAMS, NFL_TEAMS, NBA_TEAMS
    except ImportError:
        NHL_TEAMS = NFL_TEAMS = NBA_TEAMS = {}

NHL_STATIC_ELO = {
    "COL": 1620, "CAR": 1590, "DAL": 1585, "BUF": 1570,
    "FLA": 1560, "VGK": 1555, "MIN": 1545, "MTL": 1540,
    "TBL": 1535, "NYR": 1530, "EDM": 1525, "WPG": 1520,
    "BOS": 1515, "LAK": 1510, "NSH": 1505, "PHI": 1500,
    "SEA": 1495, "VAN": 1490, "NYI": 1485, "WSH": 1480,
    "PIT": 1475, "DET": 1470, "CBJ": 1465, "OTT": 1460,
    "CGY": 1455, "TOR": 1450, "CHI": 1445, "ANA": 1440,
    "SJS": 1435, "UTA": 1430, "NJD": 1425,
}

NFL_STATIC_ELO = {
    "DEN": 1610, "NE": 1600, "SEA": 1590, "JAX": 1580,
    "BUF": 1570, "HOU": 1560, "LAR": 1550, "SF": 1540,
    "CHI": 1530, "LAC": 1520, "PHI": 1510, "PIT": 1500,
    "GB": 1490, "DET": 1480, "MIN": 1470, "ATL": 1460,
    "BAL": 1450, "CAR": 1440, "TB": 1430, "IND": 1420,
    "DAL": 1410, "MIA": 1400, "CIN": 1390, "KC": 1380,
    "NO": 1370, "CLE": 1360, "WAS": 1350, "NYG": 1340,
    "ARI": 1330, "LV": 1320, "NYJ": 1310, "TEN": 1300,
}


def _schedule_path(sport: str) -> str:
    """Return best available schedule path (combined file or first per-season file)."""
    from pathlib import Path
    mapping = {
        "NHL": "data/nhl_games.csv",
        "NFL": "data/nfl_games.csv",
        "NBA": "data/nba_games.csv",
    }
    combined = mapping.get(sport, f"data/{sport.lower()}_games.csv")
    if Path(combined).exists():
        return combined

    # Fall back to any per-season file so callers still get a valid path
    sport_l = sport.lower()
    season_dir = Path(f"data/{sport_l}")
    if season_dir.is_dir():
        files = sorted(season_dir.glob(f"{sport_l}_*.csv"))
        if not files:
            files = sorted(season_dir.glob("*.csv"))
        if files:
            return str(files[-1])  # most recent
    return combined


def get_available_seasons(sport: str) -> List[str]:
    """Prefer per-season folders; fall back to combined CSV (legacy)."""
    sport_l = sport.lower()

    # 1. Per-season directory (preferred – combined CSVs are being removed)
    season_dir = Path(f"data/{sport_l}")
    if season_dir.is_dir():
        files = sorted(season_dir.glob(f"{sport_l}_*.csv"))
        if not files:
            files = sorted(season_dir.glob("*.csv"))
        seasons = [f.stem.split("_")[-1] for f in files]
        if seasons:
            return sorted(set(seasons))

    # 2. Legacy combined CSV
    path = _schedule_path(sport)
    try:
        df = pd.read_csv(path)
        if "season" in df.columns:
            seasons = sorted({str(s) for s in df["season"].dropna().unique()})
            if seasons:
                return seasons
    except Exception:
        pass

    if sport in ("NHL", "NBA"):
        return ["2025-26"]
    return ["2025"]



def get_simulatable_seasons(sport: str) -> List[str]:
    """Seasons the user may select as simulation target (excludes earliest seed year)."""
    all_seasons = get_available_seasons(sport)
    if len(all_seasons) <= 1:
        return all_seasons
    return all_seasons[1:]


def get_seed_season(sport: str) -> Optional[str]:
    all_seasons = get_available_seasons(sport)
    return all_seasons[0] if all_seasons else None


def get_base_initial_ratings(
    sport: str,
    *,
    rating_source: str = "playoffs",
    rating_basis: str = "record",
    apply_regression: bool = False,
    regression_strength: float = 0.25,
    mean_elo: float = 1500.0,
) -> Dict[str, float]:
    """Ranking-based prior from the seed year (warm-up usually starts from {})."""
    return get_initial_ratings(
        sport,
        season=get_seed_season(sport),
        rating_source=rating_source,
        rating_basis=rating_basis,
        apply_regression=apply_regression,
        regression_strength=regression_strength,
        mean_elo=mean_elo,
    )


def _get_previous_season(sport: str, current: str) -> Optional[str]:
    seasons = get_available_seasons(sport)
    if current not in seasons:
        return None
    idx = seasons.index(current)
    return seasons[idx - 1] if idx > 0 else None


def _load_season_games(sport: str, season: str) -> Optional[pd.DataFrame]:
    path = _schedule_path(sport)
    try:
        df = pd.read_csv(path)
        if "season" in df.columns:
            sub = df[df["season"].astype(str) == str(season)]
            if not sub.empty:
                return sub
    except Exception:
        pass

    for c in [
        Path(f"data/{sport.lower()}/{sport.lower()}_{season}.csv"),
        Path(f"data/{sport.lower()}/{season}.csv"),
    ]:
        if c.exists():
            try:
                return pd.read_csv(c)
            except Exception:
                continue
    return None


def _regular_season_ranking(sport: str, season: str) -> Dict[str, float]:
    df = _load_season_games(sport, season)
    if df is None or df.empty:
        return {}

    records: Dict[str, list] = {}
    for _, row in df.iterrows():
        home = str(row.get("home_team", "")).strip()
        away = str(row.get("away_team", "")).strip()
        if not home or not away:
            continue
        hs, as_ = row.get("home_score"), row.get("away_score")
        if pd.isna(hs) or pd.isna(as_):
            continue
        records.setdefault(home, [0, 0])
        records.setdefault(away, [0, 0])
        records[home][1] += 1
        records[away][1] += 1
        if hs > as_:
            records[home][0] += 1
        elif as_ > hs:
            records[away][0] += 1

    return {
        t: wins - (games - wins)
        for t, (wins, games) in records.items()
        if games > 0
    }


def _playoff_ranking(sport: str, season: str) -> Dict[str, float]:
    return _regular_season_ranking(sport, season)


def _record_to_elo(ranking: Dict[str, float], mean_elo: float = 1500.0) -> Dict[str, float]:
    if not ranking:
        return {}
    ordered = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    n = len(ordered)
    step = 300 / max(n - 1, 1)
    return {team: mean_elo + 150 - i * step for i, (team, _) in enumerate(ordered)}


def _elo_from_previous_season(sport: str, season: str) -> Dict[str, float]:
    return _record_to_elo(_regular_season_ranking(sport, season))


def get_initial_ratings(
    sport: str,
    schedule_path: Optional[str] = None,
    *,
    season: Optional[str] = None,
    rating_source: str = "playoffs",
    rating_basis: str = "record",
    apply_regression: bool = False,
    regression_strength: float = 0.25,
    mean_elo: float = 1500.0,
) -> Dict[str, float]:
    if schedule_path is None:
        schedule_path = _schedule_path(sport)

    schedule_teams: List[str] = []
    try:
        schedule = pd.read_csv(schedule_path)
        schedule_teams = (
            pd.concat([schedule["home_team"], schedule["away_team"]])
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
    except Exception:
        if sport == "NHL":
            schedule_teams = list(NHL_TEAMS.keys())
        elif sport == "NFL":
            schedule_teams = list(NFL_TEAMS.keys())
        elif sport == "NBA":
            schedule_teams = list(NBA_TEAMS.keys())

    final: Dict[str, float] = {t: mean_elo for t in schedule_teams}

    raw: Dict[str, float] = {}
    if season is not None:
        prev = _get_previous_season(sport, str(season))
        if prev is not None:
            ranking = (
                _playoff_ranking(sport, prev)
                if rating_source == "playoffs"
                else _regular_season_ranking(sport, prev)
            )
            raw = (
                _elo_from_previous_season(sport, prev)
                if rating_basis == "elo"
                else _record_to_elo(ranking, mean_elo=mean_elo)
            )
            if apply_regression and raw:
                raw = {
                    t: (1.0 - regression_strength) * e + regression_strength * mean_elo
                    for t, e in raw.items()
                }

    if raw:
        upper_map = {t.upper(): t for t in final}
        for t, e in raw.items():
            if t in final:
                final[t] = float(e)
            elif t.upper() in upper_map:
                final[upper_map[t.upper()]] = float(e)
            else:
                final[t] = float(e)

    base = NHL_STATIC_ELO if sport == "NHL" else (NFL_STATIC_ELO if sport == "NFL" else {})
    upper_map = {t.upper(): t for t in final}
    for abbr, elo in base.items():
        if abbr in final and final[abbr] == mean_elo:
            final[abbr] = float(elo)
        elif abbr.upper() in upper_map and final[upper_map[abbr.upper()]] == mean_elo:
            final[upper_map[abbr.upper()]] = float(elo)

    return final
