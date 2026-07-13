# MultiSport Elo Lab

A modular, configuration-driven Elo rating and simulation platform for sports modeling, historical backtesting, Monte Carlo simulation, parameter optimization, and model evaluation.

Version 5 established the core Elo engine architecture with a unified execution pipeline and configuration-driven behavior.  
Version 6 introduced an interactive Streamlit dashboard.  
**Version 7** adds significant improvements to parameter optimization and introduces the **Elevation Edge** adjustment.

## Version 7 Dashboard

The interactive Streamlit dashboard provides a user-friendly interface for configuring and exploring Elo models.

### Key Features

- **Adjustment Selection**: Enable or disable model adjustments (Home Field Advantage, Margin of Victory, and Elevation Edge) directly from the sidebar.
- **Parameter Optimization**: Selectively optimize parameters for any subset of enabled adjustments. The system runs a grid search over the chosen parameters and applies the best-found values to the simulation.
- **Elevation Edge**: A signature adjustment that gives the home team an advantage when playing at higher elevation using a binning system (to avoid overfitting to raw elevation values).
- **Live Progress Feedback**: Simulations (including optimization) now display progress in the sidebar using `st.status()` and a progress bar.
- **Configuration Visibility**: The Model Configuration tab and result tabs clearly show which adjustments and parameters were used for each run.

### Dashboard Tabs

1. **Model Configuration**  
   Displays the selected sport, season, simulation count, active adjustments, and (when applicable) the optimized parameters used in the last run.

2. **Season Simulation**  
   Runs Monte Carlo season simulations with support for optimized parameters.  
   Features include expected win summaries, team win distributions, median wins, standard deviation, and 90% simulation ranges.

3. **Elo Ratings**  
   Visualizes postgame Elo ratings from historical backtests with conference and division filtering.

4. **Elo Evolution**  
   Shows both historical Elo trajectories and simulated Elo paths from Monte Carlo simulations, including uncertainty bands.

5. **Model Evaluation**  
   Compares model performance using Accuracy, Log Loss, and Brier Score.

## Version 5 Architecture

The core principle of the system is that the engine is the only component that orchestrates Elo execution. All other components are configuration, transformations, evaluation utilities, or workflow orchestration.

The public engine API is:

```python
run_game(home_elo, away_elo, context, config)

Note: This project is under active development. The current focus is on refining the modeling system and dashboard experience for NFL, with plans to expand to additional seasons and other leagues (starting with NHL and NBA) in future versions.