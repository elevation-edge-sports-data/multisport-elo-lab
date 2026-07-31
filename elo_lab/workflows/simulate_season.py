"""
simulate_season.py – Version 9

Multiseason + NBA support:
  - Guards max_week filter when schedule has no "week" column
  - NBA entry in local SPORT_CONFIGS (wins-based like NFL)
  - Safe team Elo lookup (fills missing teams at 1500)
  - Compatible with per-season schedule files under data/{sport}/
"""

import pandas as pd
import numpy as np

# Try multiple import paths to stay compatible with engine structure
try:
    from elo_lab.engine.core import compute_pregame, run_game
except ImportError:
    try:
        from elo_lab.engine import compute_pregame, run_game
    except ImportError:
        def compute_pregame(home_elo, away_elo, context, config):
            return {"p_home": 0.5 + (home_elo - away_elo) / 2000}

        def run_game(home_elo, away_elo, context, config):
            k = config.get("k", 20) if config else 20
            actual = context.get("actual", 0)
            if actual == 1:
                return {"home_elo_post": home_elo + k, "away_elo_post": away_elo - k}
            else:
                return {"home_elo_post": home_elo - k, "away_elo_post": away_elo + k}


# ==================== SPORT CONFIG ====================
# Local defaults – schedule_path is a fallback only.
# Preferred path resolution lives in app/services/simulation_service.py
# (per-season files under data/{sport}/).
SPORT_CONFIGS = {
    "NFL": {
        "schedule_path": "data/nfl_games.csv",
        "max_week": 18,
        "outcome_type": "wins",
        "ot_rate": 0.0,
        "points_per_win": 1,
        "points_per_ot_loss": 0,
    },
    "NHL": {
        "schedule_path": "data/nhl_games.csv",
        "max_week": None,
        "outcome_type": "points",
        "ot_rate": 0.23,
        "points_per_win": 2,
        "points_per_ot_loss": 1,
    },
    "NBA": {
        "schedule_path": "data/nba_games.csv",
        "max_week": None,
        "outcome_type": "wins",
        "ot_rate": 0.0,
        "points_per_win": 1,
        "points_per_ot_loss": 0,
    },
}

# ---------------------------------------------------------------------------
# Schedule normalizer – map Basketball-Reference / legacy schemas
# to canonical columns: home_team, away_team, home_score, away_score
# ---------------------------------------------------------------------------

def _build_name_to_abbr(sport: str) -> dict:
    """Map full team name (and abbr) -> abbr using metadata when available."""
    mapping = {}
    try:
        from metadata import load_teams
        teams = load_teams(sport)
        for abbr, info in teams.items():
            mapping[abbr.upper()] = abbr
            mapping[abbr] = abbr
            name = info.get("name", "")
            if name:
                mapping[name] = abbr
                mapping[name.upper()] = abbr
                # common short forms
                mapping[name.replace(" ", "").upper()] = abbr
    except Exception:
        pass
    return mapping


def normalize_schedule(df: pd.DataFrame, sport: str = "NFL") -> pd.DataFrame:
    """
    Convert various schedule schemas into canonical columns:
      home_team, away_team, home_score, away_score  (+ season, week if present)

    Supported input formats:
      - Legacy combined: home_team / away_team / home_score / away_score
      - NBA B-R: Visitor/Neutral, PTS, Home/Neutral, PTS
      - NHL B-R: Visitor, G, Home, G
      - NFL B-R: Winner/tie, Loser/tie, Pts, Pts  (home unknown – treat winner as home)
    """
    df = df.copy()
    cols = {c.strip(): c for c in df.columns}
    lower = {c.lower().strip(): c for c in df.columns}

    name_map = _build_name_to_abbr(sport)

    def to_abbr(val):
        s = str(val).strip()
        if s in name_map:
            return name_map[s]
        if s.upper() in name_map:
            return name_map[s.upper()]
        return s  # leave as-is if unknown

    # Already canonical
    if "home_team" in df.columns and "away_team" in df.columns:
        for col in ("home_team", "away_team"):
            df[col] = df[col].map(to_abbr)
        return df

    # NBA: Visitor/Neutral, PTS, Home/Neutral, PTS  (duplicate PTS names)
    if "Visitor/Neutral" in df.columns and "Home/Neutral" in df.columns:
        # pandas renames duplicate PTS to PTS and PTS.1
        pts_cols = [c for c in df.columns if c == "PTS" or c.startswith("PTS")]
        away_pts = pts_cols[0] if pts_cols else None
        home_pts = pts_cols[1] if len(pts_cols) > 1 else None
        out = pd.DataFrame()
        out["away_team"] = df["Visitor/Neutral"].map(to_abbr)
        out["home_team"] = df["Home/Neutral"].map(to_abbr)
        if away_pts:
            out["away_score"] = pd.to_numeric(df[away_pts], errors="coerce")
        if home_pts:
            out["home_score"] = pd.to_numeric(df[home_pts], errors="coerce")
        if "Date" in df.columns:
            out["date"] = df["Date"]
        return out

    # NHL B-R: Visitor, G, Home, G
    if "Visitor" in df.columns and "Home" in df.columns:
        g_cols = [c for c in df.columns if c == "G" or c.startswith("G")]
        away_g = g_cols[0] if g_cols else None
        home_g = g_cols[1] if len(g_cols) > 1 else None
        out = pd.DataFrame()
        out["away_team"] = df["Visitor"].map(to_abbr)
        out["home_team"] = df["Home"].map(to_abbr)
        if away_g:
            out["away_score"] = pd.to_numeric(df[away_g], errors="coerce")
        if home_g:
            out["home_score"] = pd.to_numeric(df[home_g], errors="coerce")
        if "Date" in df.columns:
            out["date"] = df["Date"]
        return out

    # NFL B-R: Winner/tie, Loser/tie, Pts, Pts  (no home/away – use winner as home proxy)
    if "Winner/tie" in df.columns and "Loser/tie" in df.columns:
        pts_cols = [c for c in df.columns if c.lower().startswith("pts")]
        # columns often: Pts (winner), Pts.1 (loser) after pandas load
        w_pts = pts_cols[0] if pts_cols else None
        l_pts = pts_cols[1] if len(pts_cols) > 1 else None
        out = pd.DataFrame()
        out["home_team"] = df["Winner/tie"].map(to_abbr)
        out["away_team"] = df["Loser/tie"].map(to_abbr)
        if w_pts:
            out["home_score"] = pd.to_numeric(df[w_pts], errors="coerce")
        if l_pts:
            out["away_score"] = pd.to_numeric(df[l_pts], errors="coerce")
        if "Week" in df.columns:
            out["week"] = df["Week"]
        if "Date" in df.columns:
            out["date"] = df["Date"]
        return out

    raise ValueError(
        f"Unrecognized schedule schema. Columns: {list(df.columns)}. "
        "Expected home_team/away_team or Basketball-Reference format."
    )





def simulate_season(
    schedule_path=None,
    config=None,
    seed=42,
    initial_ratings=None,
    sport="NFL",
):
    """Core season simulation with sport support (NHL points + OT, NFL/NBA wins)."""
    cfg = SPORT_CONFIGS.get(sport, SPORT_CONFIGS["NFL"])
    if schedule_path is None:
        schedule_path = cfg["schedule_path"]

    try:
        schedule = pd.read_csv(schedule_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Schedule file not found: {schedule_path}\n"
            "→ Prefer per-season files under data/{sport}/ "
            "(e.g. data/nba/nba_2025.csv). Combined CSVs are legacy."
        )

    schedule = normalize_schedule(schedule, sport=sport)

    # If a multi-season file was passed, keep only the first season present
    # (caller should already filter via simulation_service when a season is selected)
    if "season" in schedule.columns and schedule["season"].nunique() > 1:
        schedule = schedule[schedule["season"] == schedule["season"].iloc[0]]

    # Guard: only filter by week when the column exists (NBA schedules often lack it)
    if cfg.get("max_week") and "week" in schedule.columns:
        schedule = schedule[pd.to_numeric(schedule["week"], errors="coerce") <= cfg["max_week"]]

    sort_cols = []
    if "season" in schedule.columns:
        sort_cols.append("season")
    if "week" in schedule.columns:
        sort_cols.append("week")
    if sort_cols:
        schedule = schedule.sort_values(sort_cols)
    else:
        schedule = schedule.reset_index(drop=True)

    rng = np.random.default_rng(seed)

    # Collect every team that appears in this schedule
    schedule_teams = (
        pd.concat([schedule["home_team"], schedule["away_team"]])
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    if initial_ratings is None:
        initial_ratings = {team: 1500.0 for team in schedule_teams}
    else:
        # Ensure every schedule team has an entry (prevents KeyError)
        initial_ratings = dict(initial_ratings)
        for team in schedule_teams:
            if team not in initial_ratings:
                # try case-insensitive match
                upper_map = {k.upper(): k for k in initial_ratings}
                if team.upper() in upper_map:
                    initial_ratings[team] = initial_ratings[upper_map[team.upper()]]
                else:
                    initial_ratings[team] = 1500.0

    team_elo = {t: float(initial_ratings[t]) for t in schedule_teams}
    # also keep any extra keys from initial_ratings
    for t, e in initial_ratings.items():
        if t not in team_elo:
            team_elo[t] = float(e)

    wins = {team: 0 for team in team_elo}
    points = {team: 0 for team in team_elo}
    losses = {team: 0 for team in team_elo}

    elo_history = []
    game_number = 0

    for _, game in schedule.iterrows():
        home = str(game["home_team"]).strip()
        away = str(game["away_team"]).strip()
        week = game["week"] if "week" in game.index and pd.notna(game.get("week")) else (game_number // 2 + 1)
        game_number += 1

        # Safety – should never hit after the fill above
        if home not in team_elo:
            team_elo[home] = 1500.0
            wins[home] = losses[home] = points[home] = 0
        if away not in team_elo:
            team_elo[away] = 1500.0
            wins[away] = losses[away] = points[away] = 0

        pregame = compute_pregame(
            home_elo=team_elo[home],
            away_elo=team_elo[away],
            context={
                "season": game.get("season"),
                "week": week,
                "home_team": home,
                "away_team": away,
            },
            config=config,
        )

        p_home = pregame.get("p_home", 0.5)
        actual_home_win = int(rng.random() < p_home)

        result = run_game(
            home_elo=team_elo[home],
            away_elo=team_elo[away],
            context={
                "season": game.get("season"),
                "week": week,
                "home_team": home,
                "away_team": away,
                "home_score": actual_home_win,
                "away_score": 1 - actual_home_win,
                "actual": actual_home_win,
            },
            config=config,
        )

        team_elo[home] = result["home_elo_post"]
        team_elo[away] = result["away_elo_post"]

        elo_history.append({
            "team": home,
            "elo": team_elo[home],
            "week": week,
            "game_number": game_number,
            "games_played": game_number // 2 + 1,
        })
        elo_history.append({
            "team": away,
            "elo": team_elo[away],
            "week": week,
            "game_number": game_number,
            "games_played": game_number // 2 + 1,
        })

        if cfg.get("outcome_type") == "points":
            # NHL: 2 points for win, 1 for OT loss
            goes_to_ot = rng.random() < cfg.get("ot_rate", 0.0)
            if actual_home_win:
                wins[home] += 1
                points[home] += cfg.get("points_per_win", 2)
                if goes_to_ot:
                    points[away] += cfg.get("points_per_ot_loss", 1)
                else:
                    losses[away] += 1
            else:
                wins[away] += 1
                points[away] += cfg.get("points_per_win", 2)
                if goes_to_ot:
                    points[home] += cfg.get("points_per_ot_loss", 1)
                else:
                    losses[home] += 1
        else:
            # NFL / NBA: standard win/loss
            if actual_home_win:
                wins[home] += 1
                losses[away] += 1
            else:
                wins[away] += 1
                losses[home] += 1

    standings = pd.DataFrame({
        "team": list(team_elo.keys()),
        "wins": [wins.get(t, 0) for t in team_elo],
        "losses": [losses.get(t, 0) for t in team_elo],
        "points": [points.get(t, wins.get(t, 0)) for t in team_elo],
        "elo": [team_elo[t] for t in team_elo],
    })

    return standings, team_elo, pd.DataFrame(elo_history)


def simulate_many_seasons(
    n_sims=500,
    schedule_path=None,
    config=None,
    seed=42,
    initial_ratings=None,
    sport="NFL",
):
    cfg = SPORT_CONFIGS.get(sport, SPORT_CONFIGS["NFL"])
    if schedule_path is None:
        schedule_path = cfg["schedule_path"]

    results = []
    for i in range(n_sims):
        standings, _, _ = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
            initial_ratings=initial_ratings,
            sport=sport,
        )
        for _, row in standings.iterrows():
            results.append({
                "sim_id": i,
                "team": row["team"],
                "wins": int(row["wins"]),
                "points": int(row.get("points", row["wins"])),
            })
    return pd.DataFrame(results)


def simulate_elo_evolution(
    n_sims=500,
    schedule_path=None,
    config=None,
    seed=42,
    initial_ratings=None,
    sport="NFL",
):
    cfg = SPORT_CONFIGS.get(sport, SPORT_CONFIGS["NFL"])
    if schedule_path is None:
        schedule_path = cfg["schedule_path"]

    history = []
    for i in range(n_sims):
        _, _, elo_hist = simulate_season(
            schedule_path=schedule_path,
            config=config,
            seed=seed + i,
            initial_ratings=initial_ratings,
            sport=sport,
        )
        elo_hist["sim_id"] = i
        history.append(elo_hist)

    history = pd.concat(history, ignore_index=True)
    group_col = "games_played" if "games_played" in history.columns else "week"

    evolution = (
        history.groupby(["sim_id", "team", group_col])["elo"]
        .last()
        .reset_index()
        .groupby(["team", group_col])["elo"]
        .agg(
            mean_elo="mean",
            p05_elo=lambda x: x.quantile(0.05),
            p95_elo=lambda x: x.quantile(0.95),
        )
        .reset_index()
        .sort_values(["team", group_col])
    )
    return evolution.rename(columns={group_col: "games_played"})


def summarize_simulations(sim_results):
    agg_spec = {
        "median_wins": ("wins", "median"),
        "mean_wins": ("wins", "mean"),
    }
    if "points" in sim_results.columns:
        agg_spec["mean_points"] = ("points", "mean")
        agg_spec["median_points"] = ("points", "median")
    return sim_results.groupby("team").agg(**agg_spec).reset_index()


def win_distributions(sim_results):
    return sim_results
