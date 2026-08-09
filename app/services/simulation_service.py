import pandas as pd
import tempfile
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Use the multi-sport playoff wrapper
# ---------------------------------------------------------------------------
from elo_lab.workflows.simulate_with_playoffs import simulate_many_seasons

from elo_lab.workflows.simulate_season import (
    summarize_simulations,
    win_distributions,
)

try:
    from elo_lab.configuration.sport_configs import SPORT_CONFIGS
except ImportError:
    SPORT_CONFIGS = {}

try:
    from metadata.nhl_teams import NHL_TEAMS
except ImportError:
    NHL_TEAMS = {}


def _resolve_schedule_path(sport: str, season=None) -> tuple:
    """
    Return (schedule_path, tmp_path_or_None).

    Preference (combined CSVs are temporary / being removed):
      1. Per-season file for the requested season under data/{sport}/
      2. Concatenate all per-season files under data/{sport}/ (optionally filter)
      3. Combined CSV (legacy fallback while visualizations still need it)
    """
    sport_l = sport.lower()
    season_dir = Path(f"data/{sport_l}")

    # 1. Specific per-season file
    if season is not None and season_dir.is_dir():
        candidates = [
            season_dir / f"{sport_l}_{season}.csv",
            season_dir / f"{season}.csv",
        ]
        for c in candidates:
            if c.exists():
                return str(c), None

    # 2. Build from all per-season files
    if season_dir.is_dir():
        files = sorted(season_dir.glob(f"{sport_l}_*.csv"))
        if not files:
            files = sorted(season_dir.glob("*.csv"))
        frames = []
        for f in files:
            try:
                df = pd.read_csv(f)
                if "season" not in df.columns:
                    year = f.stem.split("_")[-1]
                    df["season"] = year
                frames.append(df)
            except Exception:
                continue
        if frames:
            combined_df = pd.concat(frames, ignore_index=True)
            if season is not None and "season" in combined_df.columns:
                combined_df = combined_df[
                    combined_df["season"].astype(str) == str(season)
                ]
            if not combined_df.empty:
                tmp = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False, newline=""
                )
                combined_df.to_csv(tmp.name, index=False)
                tmp.close()
                return tmp.name, tmp.name

    # 3. Legacy combined CSV
    combined = {
        "NHL": "data/nhl_games.csv",
        "NFL": "data/nfl_games.csv",
        "NBA": "data/nba_games.csv",
    }.get(sport, f"data/{sport_l}_games.csv")

    cfg = SPORT_CONFIGS.get(sport, {})
    if cfg.get("schedule_path"):
        combined = cfg["schedule_path"]

    if Path(combined).exists():
        if season is None:
            return combined, None
        try:
            df = pd.read_csv(combined)
            if "season" in df.columns:
                filtered = df[df["season"].astype(str) == str(season)]
                if not filtered.empty:
                    tmp = tempfile.NamedTemporaryFile(
                        mode="w", suffix=".csv", delete=False, newline=""
                    )
                    filtered.to_csv(tmp.name, index=False)
                    tmp.close()
                    return tmp.name, tmp.name
        except Exception:
            pass
        return combined, None

    return combined, None


def calculate_achievement_probabilities(sim_results: pd.DataFrame, sport: str) -> pd.DataFrame:
    if sim_results.empty:
        return pd.DataFrame(columns=[
            "team", "make_playoffs", "home_ice",
            "first_in_division", "first_in_conference", "first_in_league",
        ])

    all_results = []

    for sim_id in sim_results["sim_id"].unique():
        sim_data = sim_results[sim_results["sim_id"] == sim_id].copy()

        if sport == "NHL":
            team_lookup = {}
            for abbr, data in NHL_TEAMS.items():
                team_lookup[abbr.lower().strip()] = data
                team_lookup[data["name"].lower().strip()] = data

            def get_meta(team_name):
                key = str(team_name).lower().strip()
                return team_lookup.get(key, {})

            sim_data["conference"] = sim_data["team"].apply(
                lambda x: get_meta(x).get("conference")
            )
            sim_data["division"] = sim_data["team"].apply(
                lambda x: get_meta(x).get("division")
            )

            matched = sim_data.dropna(subset=["conference", "division"]).copy()
            if matched.empty:
                continue

            matched = matched.sort_values("points", ascending=False)

            qualified = set()
            home_ice = set()
            first_div = set()
            first_conf = set()

            for conf in ["Eastern", "Western"]:
                conf_teams = matched[matched["conference"] == conf]
                qualified.update(conf_teams.head(8)["team"].tolist())

            for _, group in matched.groupby(["conference", "division"]):
                home_ice.update(group.head(2)["team"].tolist())

            for _, group in matched.groupby(["conference", "division"]):
                if not group.empty:
                    first_div.add(group.iloc[0]["team"])

            for conf in ["Eastern", "Western"]:
                conf_teams = matched[matched["conference"] == conf]
                if not conf_teams.empty:
                    first_conf.add(conf_teams.iloc[0]["team"])

            first_league = matched.iloc[0]["team"] if not matched.empty else None

            sim_data["make_playoffs"] = sim_data["team"].isin(qualified)
            sim_data["home_ice"] = sim_data["team"].isin(home_ice)
            sim_data["first_in_division"] = sim_data["team"].isin(first_div)
            sim_data["first_in_conference"] = sim_data["team"].isin(first_conf)
            sim_data["first_in_league"] = sim_data["team"] == first_league

        else:
            # NFL / NBA – top 7 by wins (placeholder until richer logic is needed)
            sim_data = sim_data.sort_values("wins", ascending=False)
            n = min(7, len(sim_data))
            sim_data["make_playoffs"] = False
            sim_data.iloc[:n, sim_data.columns.get_loc("make_playoffs")] = True
            for col in [
                "home_ice", "first_in_division",
                "first_in_conference", "first_in_league",
            ]:
                sim_data[col] = False

        all_results.append(sim_data[[
            "sim_id", "team", "make_playoffs", "home_ice",
            "first_in_division", "first_in_conference", "first_in_league",
        ]])

    if not all_results:
        return pd.DataFrame(columns=[
            "team", "make_playoffs", "home_ice",
            "first_in_division", "first_in_conference", "first_in_league",
        ])

    df = pd.concat(all_results, ignore_index=True)

    prob_df = df.groupby("team").agg(
        make_playoffs=("make_playoffs", "mean"),
        home_ice=("home_ice", "mean"),
        first_in_division=("first_in_division", "mean"),
        first_in_conference=("first_in_conference", "mean"),
        first_in_league=("first_in_league", "mean"),
    ).reset_index()

    for col in prob_df.columns:
        if col != "team":
            prob_df[col] = (prob_df[col] * 100).round(1)

    return prob_df


def run_simulation(
    config,
    n_sims,
    initial_ratings=None,
    sport="NFL",
    season=None,
    from_season=None,
    seed: int = 42,
    inter_season_regression: float = 0.35,
    progress_callback=None,
):
    """
    When season is set: warm Elo on actual recent seasons, then MC the target.
    When season is None: legacy single-pass path (prior-only style).

    from_season : optional start of the warm-up window (inclusive).
                  History runs from from_season through the season before
                  the target. If None, falls back to the previous default
                  of max 2 history seasons.
    seed : RNG seed for reproducible Monte Carlo draws.
    inter_season_regression : pull toward mean_elo after each warm-up season
                  (0.35 default; previously 0.67 which erased recent form).
    progress_callback : callable, optional
        Called as progress_callback(fraction: float) with fraction in [0, 1]
        during Monte Carlo work (approximately 10% steps).
    """
    tmp_path = None
    try:
        if season is not None:
            from elo_lab.workflows.simulate_season import simulate_many_seasons_multiyear
            try:
                from services.initial_ratings_service import get_available_seasons
            except ImportError:
                from app.services.initial_ratings_service import get_available_seasons

            # Map explicit from_season → max_history_seasons
            max_history = 2  # legacy default
            if from_season is not None:
                all_seasons = get_available_seasons(sport)
                if (
                    from_season in all_seasons
                    and str(season) in all_seasons
                ):
                    from_idx = all_seasons.index(from_season)
                    target_idx = all_seasons.index(str(season))
                    # number of seasons in [from_season, target)
                    max_history = max(1, target_idx - from_idx)

            # Single target-season Monte Carlo + collect per-sim standings/Elo
            # so playoffs reuse the exact same outcomes (no second full pass).
            def _multi_progress(frac):
                if progress_callback is not None:
                    try:
                        # Regular-season phase ≈ 0–85% of reported progress
                        progress_callback(0.85 * float(frac))
                    except Exception:
                        pass

            sim_results, elo_evolution, season_results = simulate_many_seasons_multiyear(
                n_sims=n_sims,
                sport=sport,
                target_season=str(season),
                config=config,
                seed=int(seed),
                base_initial_ratings=initial_ratings or {},
                return_elo_evolution=True,
                return_season_results=True,
                hybrid_warmup=True,
                inter_season_regression=float(inter_season_regression),
                playoff_k_multiplier=1.75,
                include_playoffs_in_warmup=True,
                max_history_seasons=max_history,
                progress_callback=_multi_progress,
            )

            # Playoffs from the collected target-season outcomes only
            _, playoff_probs, _ = simulate_many_seasons(
                n_sims=n_sims,  # ignored when season_results is supplied
                config=config,
                seed=int(seed),
                sport=sport,
                season_results=season_results,
                progress_callback=progress_callback,
            )
        else:
            schedule_path, tmp_path = _resolve_schedule_path(sport, season)
            sim_results, playoff_probs, elo_evolution = simulate_many_seasons(
                n_sims=n_sims,
                schedule_path=schedule_path,
                config=config,
                seed=int(seed),
                initial_ratings=initial_ratings,
                sport=sport,
                progress_callback=progress_callback,
            )

        summary = summarize_simulations(sim_results)
        distributions = win_distributions(sim_results)
        achievement_probs = calculate_achievement_probabilities(sim_results, sport)

        return {
            "summary": summary,
            "distribution": distributions,
            "elo_evolution": elo_evolution,
            "achievement_probs": achievement_probs,
            "playoff_probs": playoff_probs,
            "raw_sim_results": sim_results,
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
