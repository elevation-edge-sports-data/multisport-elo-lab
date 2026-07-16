import pandas as pd
from elo_lab.workflows.simulate_season import (
    simulate_many_seasons,
    simulate_elo_evolution,
    summarize_simulations,
    win_distributions,
)

from metadata.nhl_teams import NHL_TEAMS
from metadata.nfl_teams import NFL_TEAMS


def calculate_achievement_probabilities(sim_results: pd.DataFrame, sport: str) -> pd.DataFrame:
    if sim_results.empty:
        cols = ["team", "make_playoffs", "first_in_division", "first_in_conference", "first_in_league"]
        if sport == "NHL":
            cols.insert(2, "home_ice")
        return pd.DataFrame(columns=cols)

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

            all_results.append(sim_data[[
                "sim_id", "team", "make_playoffs", "home_ice",
                "first_in_division", "first_in_conference", "first_in_league"
            ]])

        else:
            # NFL: proper playoff structure (7 teams per conference)
            # Division winners + 3 wild cards per conference
            team_lookup = {}
            for abbr, data in NFL_TEAMS.items():
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

            # Sort by wins descending (primary; secondary not needed for sims as ties rare)
            matched = matched.sort_values("wins", ascending=False)

            qualified = set()
            first_div = set()
            first_conf = set()

            # Per conference (AFC / NFC)
            for conf in ["AFC", "NFC"]:
                conf_teams = matched[matched["conference"] == conf].copy()
                if conf_teams.empty:
                    continue

                # Division winners (top team in each of 4 divisions)
                div_winners = []
                for div in ["East", "North", "South", "West"]:
                    div_group = conf_teams[conf_teams["division"] == div]
                    if not div_group.empty:
                        winner = div_group.iloc[0]["team"]
                        div_winners.append(winner)
                        first_div.add(winner)

                # Remaining teams for wild cards (exclude division winners)
                remaining = conf_teams[~conf_teams["team"].isin(div_winners)]
                wild_cards = remaining.head(3)["team"].tolist()

                qualified.update(div_winners)
                qualified.update(wild_cards)

                # First in Conference = top team overall in conf (by wins)
                if not conf_teams.empty:
                    first_conf.add(conf_teams.iloc[0]["team"])

            # First in League = overall best record
            first_league = matched.iloc[0]["team"] if not matched.empty else None

            # No "home_ice" for NFL (home-field is for #1 seeds / conference winners, but not tracked as top-2-div)
            sim_data["make_playoffs"] = sim_data["team"].isin(qualified)
            sim_data["first_in_division"] = sim_data["team"].isin(first_div)
            sim_data["first_in_conference"] = sim_data["team"].isin(first_conf)
            sim_data["first_in_league"] = sim_data["team"] == first_league
            # Explicitly set home_ice to False for consistency if needed later, but we omit it
            sim_data["home_ice"] = False

            all_results.append(sim_data[[
                "sim_id", "team", "make_playoffs", "home_ice",
                "first_in_division", "first_in_conference", "first_in_league"
            ]])

    if not all_results:
        cols = ["team", "make_playoffs", "first_in_division", "first_in_conference", "first_in_league"]
        if sport == "NHL":
            cols.insert(2, "home_ice")
        return pd.DataFrame(columns=cols)

    df = pd.concat(all_results, ignore_index=True)

    # Aggregate probabilities; for NFL drop home_ice
    agg_dict = {
        "make_playoffs": ("make_playoffs", "mean"),
        "first_in_division": ("first_in_division", "mean"),
        "first_in_conference": ("first_in_conference", "mean"),
        "first_in_league": ("first_in_league", "mean"),
    }
    if sport == "NHL":
        agg_dict["home_ice"] = ("home_ice", "mean")

    prob_df = df.groupby("team").agg(**agg_dict).reset_index()

    for col in prob_df.columns:
        if col != "team":
            prob_df[col] = (prob_df[col] * 100).round(1)

    # Ensure column order
    if sport == "NHL":
        prob_df = prob_df[["team", "make_playoffs", "home_ice", "first_in_division", "first_in_conference", "first_in_league"]]
    else:
        prob_df = prob_df[["team", "make_playoffs", "first_in_division", "first_in_conference", "first_in_league"]]

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