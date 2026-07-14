"""
Fixed simulate_season.py for multisport support (v8)
- Fixed broken import that was crashing the app
- Kept full NHL points + OT logic
- Compatible with original v7 engine
"""

import pandas as pd
import numpy as np

# Try multiple import paths to stay compatible with v7 structure
try:
    from elo_lab.engine.core import compute_pregame, run_game
except ImportError:
    try:
        from elo_lab.engine import compute_pregame, run_game
    except ImportError:
        # Fallback functions (basic Elo behavior)
        def compute_pregame(home_elo, away_elo, context, config):
            return {"p_home": 0.5 + (home_elo - away_elo) / 2000}

        def run_game(home_elo, away_elo, context, config):
            k = config.get("k", 20)
            actual = context.get("actual", 0)
            if actual == 1:
                return {"home_elo_post": home_elo + k, "away_elo_post": away_elo - k}
            else:
                return {"home_elo_post": home_elo - k, "away_elo_post": away_elo + k}


# ==================== SPORT CONFIG ====================
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
    }
}


def simulate_season(
    schedule_path=None,
    config=None,
    seed=42,
    initial_ratings=None,
    sport="NFL",
):
    """Core season simulation with sport support (NHL points + OT)."""
    cfg = SPORT_CONFIGS.get(sport, SPORT_CONFIGS["NFL"])
    if schedule_path is None:
        schedule_path = cfg["schedule_path"]

    try:
        schedule = pd.read_csv(schedule_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Schedule file not found: {schedule_path}\n"
            "→ For NHL testing, create data/nhl_games.csv (or use NFL for now)."
        )

    if "season" in schedule.columns:
        schedule = schedule[schedule["season"] == schedule["season"].iloc[0]]

    if cfg.get("max_week"):
        schedule = schedule[schedule["week"] <= cfg["max_week"]]

    schedule = schedule.sort_values(
        ["season", "week"] if "week" in schedule.columns else schedule.columns[0]
    )

    rng = np.random.default_rng(seed)

    if initial_ratings is None:
        teams = pd.concat([schedule["home_team"], schedule["away_team"]]).unique()
        initial_ratings = {team: 1500 for team in teams}

    team_elo = initial_ratings.copy()
    wins = {team: 0 for team in team_elo}
    points = {team: 0 for team in team_elo}
    losses = {team: 0 for team in team_elo}

    elo_history = []
    game_number = 0

    for _, game in schedule.iterrows():
        home = game["home_team"]
        away = game["away_team"]
        week = game.get("week", game_number // 2 + 1)
        game_number += 1

        pregame = compute_pregame(
            home_elo=team_elo[home],
            away_elo=team_elo[away],
            context={"season": game.get("season"), "week": week,
                     "home_team": home, "away_team": away},
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

        # Record Elo history
        elo_history.append({
            "team": home, "elo": team_elo[home],
            "week": week, "game_number": game_number,
            "games_played": game_number // 2 + 1
        })
        elo_history.append({
            "team": away, "elo": team_elo[away],
            "week": week, "game_number": game_number,
            "games_played": game_number // 2 + 1
        })

        # Sport-specific outcome handling
        if cfg["outcome_type"] == "points":
            # NHL: 2 points for win, 1 for OT loss
            goes_to_ot = rng.random() < cfg["ot_rate"]
            if actual_home_win:
                wins[home] += 1
                points[home] += cfg["points_per_win"]
                if goes_to_ot:
                    points[away] += cfg["points_per_ot_loss"]
                else:
                    losses[away] += 1
            else:
                wins[away] += 1
                points[away] += cfg["points_per_win"]
                if goes_to_ot:
                    points[home] += cfg["points_per_ot_loss"]
                else:
                    losses[home] += 1
        else:
            # NFL: standard win/loss
            if actual_home_win:
                wins[home] += 1
                losses[away] += 1
            else:
                wins[away] += 1
                losses[home] += 1

    standings = pd.DataFrame({
        "team": list(team_elo.keys()),
        "wins": [wins[t] for t in team_elo],
        "losses": [losses[t] for t in team_elo],
        "points": [points.get(t, wins[t]) for t in team_elo],
        "elo": [team_elo[t] for t in team_elo],
    })

    return standings, team_elo, pd.DataFrame(elo_history)


def simulate_many_seasons(n_sims=500, schedule_path=None, config=None,
                          seed=42, initial_ratings=None, sport="NFL"):
    cfg = SPORT_CONFIGS.get(sport, SPORT_CONFIGS["NFL"])
    if schedule_path is None:
        schedule_path = cfg["schedule_path"]

    results = []
    for i in range(n_sims):
        standings, _, _ = simulate_season(
            schedule_path=schedule_path, config=config,
            seed=seed + i, initial_ratings=initial_ratings, sport=sport
        )
        for _, row in standings.iterrows():
            results.append({
                "sim_id": i,
                "team": row["team"],
                "wins": int(row["wins"]),
                "points": int(row.get("points", row["wins"])),
            })
    return pd.DataFrame(results)


def simulate_elo_evolution(n_sims=500, schedule_path=None, config=None,
                           seed=42, initial_ratings=None, sport="NFL"):
    cfg = SPORT_CONFIGS.get(sport, SPORT_CONFIGS["NFL"])
    if schedule_path is None:
        schedule_path = cfg["schedule_path"]

    history = []
    for i in range(n_sims):
        _, _, elo_hist = simulate_season(
            schedule_path=schedule_path, config=config,
            seed=seed + i, initial_ratings=initial_ratings, sport=sport
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
        .agg(mean_elo="mean",
             p05_elo=lambda x: x.quantile(0.05),
             p95_elo=lambda x: x.quantile(0.95))
        .reset_index()
        .sort_values(["team", group_col])
    )
    return evolution.rename(columns={group_col: "games_played"})


def summarize_simulations(sim_results):
    return sim_results.groupby("team").agg(
        median_wins=("wins", "median"),
        mean_points=("points", "mean") if "points" in sim_results.columns else ("wins", "mean"),
    ).reset_index()


def win_distributions(sim_results):
    return sim_results