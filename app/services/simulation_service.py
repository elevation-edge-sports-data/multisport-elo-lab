from elo_lab.workflows.simulate_season import (
    simulate_many_seasons,
    simulate_elo_evolution,
    summarize_simulations,
    win_distributions,
)


def run_simulation(
    config,
    n_sims,
    initial_ratings=None,
):
    """
    Executes Monte Carlo season simulations and returns
    processed outputs for dashboard display.

    Parameters
    ----------
    config : dict
        Elo model configuration.

    n_sims : int
        Number of Monte Carlo simulations.

    initial_ratings : dict, optional
        Starting Elo ratings for each team.

    Returns
    -------
    dict
        Simulation outputs including:
        - raw simulation results
        - expected win summaries
        - win distributions
        - simulated Elo evolution with uncertainty bands
    """

    sim_results = simulate_many_seasons(
        n_sims=n_sims,
        config=config,
        initial_ratings=initial_ratings,
    )


    summary = summarize_simulations(
        sim_results
    )


    distributions = win_distributions(
        sim_results
    )


    elo_evolution = simulate_elo_evolution(
        n_sims=n_sims,
        config=config,
        initial_ratings=initial_ratings,
    )


    return {
        "raw": sim_results,
        "summary": summary,
        "distribution": distributions,
        "elo_evolution": elo_evolution,
    }