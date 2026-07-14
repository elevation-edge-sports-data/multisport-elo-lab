import pandas as pd
from elo_lab.workflows.simulate_season import (
    simulate_many_seasons,
    simulate_elo_evolution,
    summarize_simulations,
    win_distributions,
)

from metadata.nhl_teams import NHL_TEAMS


def calculate_achievement_probabilities(sim_results: pd.DataFrame, sport: str) -> pd.DataFrame:
    if sim_results.empty:
        return pd.DataFrame(columns=["team", "make_playoffs", "home_ice", 
                                     "first_in_division", "first_in_conference", "first_in_league"])

    all_results = []

    for sim_id in sim_results["sim_id"].unique():
        sim_data = sim_results[sim_results["sim_id"] == sim_id].copy()

        if sport == "NHL":
            # Robust matching for both abbreviations and full names
            team_lookup = {}
            for abbr, data in NHL_TEAMS.items():
                team_lookup[abbr.lower().strip()] = data
                team_lookup[data["name"].lower().strip()] = data

            def get_meta(team_name):
                key = str(team_name).lower().strip()
                return team_lookup.get(key, {})

            sim_data["conference"] = sim_data["team"].apply(lambda x: get_meta(x).get("conference"))
            sim_data["division"] = sim_data["team"].apply(lambda x: get_meta(x).get("division"))

            matched = sim_data.dropna(subset=["conference", "division"]).copy()
            if matched.empty:
                continue

            matched = matched.sort_values("points", ascending=False)

            qualified = set()
            home_ice = set()
            first_div = set()
            first_conf = set()

            # Make Playoffs
            for conf in ["Eastern", "Western"]:
                conf_teams = matched[matched["conference"] == conf]
                qualified.update(conf_teams.head(8)["team"].tolist())

            # Home Ice (Top 2 per division)
            for _, group in matched.groupby(["conference", "division"]):
                home_ice.update(group.head(2)["team"].tolist())

            # First in Division
            for _, group in matched.groupby(["conference", "division"]):
                if not group.empty:
                    first_div.add(group.iloc[0]["team"])

            # First in Conference
            for conf in ["Eastern", "Western"]:
                conf_teams = matched[matched["conference"] == conf]
                if not conf_teams.empty:
                    first_conf.add(conf_teams.iloc[0]["team"])

            # First in League
            first_league = matched.iloc[0]["team"] if not matched.empty else None

            sim_data["make_playoffs"] = sim_data["team"].isin(qualified)
            sim_data["home_ice"] = sim_data["team"].isin(home_ice)
            sim_data["first_in_division"] = sim_data["team"].isin(first_div)
            sim_data["first_in_conference"] = sim_data["team"].isin(first_conf)
            sim_data["first_in_league"] = sim_data["team"] == first_league

        else:
            # NFL placeholder
            sim_data = sim_data.sort_values("wins", ascending=False)
            n = min(7, len(sim_data))
            sim_data["make_playoffs"] = False
            sim_data.iloc[:n, sim_data.columns.get_loc("make_playoffs")] = True
            for col in ["home_ice", "first_in_division", "first_in_conference", "first_in_league"]:
                sim_data[col] = False

        all_results.append(sim_data[[
            "sim_id", "team", "make_playoffs", "home_ice",
            "first_in_division", "first_in_conference", "first_in_league"
        ]])

    if not all_results:
        return pd.DataFrame(columns=["team", "make_playoffs", "home_ice", 
                                     "first_in_division", "first_in_conference", "first_in_league"])

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


def run_simulation(config, n_sims, initial_ratings=None, sport="NFL", season=None):
    sim_results = simulate_many_seasons(
        n_sims=n_sims,
        config=config,
        initial_ratings=initial_ratings,
        sport=sport,
    )

    summary = summarize_simulations(sim_results)
    distributions = win_distributions(sim_results)
    elo_evolution = simulate_elo_evolution(
        n_sims=n_sims,
        config=config,
        initial_ratings=initial_ratings,
        sport=sport,
    )

    achievement_probs = calculate_achievement_probabilities(sim_results, sport)

    if not achievement_probs.empty:
        summary = summary.merge(achievement_probs, on="team", how="left")

    return {
        "raw": sim_results,
        "summary": summary,
        "distribution": distributions,
        "elo_evolution": elo_evolution,
        "achievement_probs": achievement_probs,
    }