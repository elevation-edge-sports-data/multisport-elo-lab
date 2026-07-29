# MultiSport Elo Lab

A modular, configuration-driven Elo rating and simulation platform for **NHL**, **NBA**, and **NFL**.

Supports historical backtesting, Monte Carlo regular-season simulation, parameter optimization, and interactive model evaluation through a Streamlit dashboard.

**Live dashboard**: [https://multisport-elo-lab.streamlit.app/](https://multisport-elo-lab.streamlit.app/)

**Current version: 10**

---

## Highlights (Version 10)

- Full multi-sport support with consistent ordering: **NHL · NBA · NFL**
- Multi-season aware initial ratings (playoffs or regular-season source, record or Elo basis, optional regression-to-mean)
- Continuous **Elevation Edge** (Elo points per 1,000 ft of altitude difference)
- Sport-specific home advantage labels (Home-Ice / Home-Court / Home-Field)
- Log5 baseline + residual diagnostics
- Parameter optimization with interactive grid-search landscape
- Regular-season achievement probabilities (Make Playoffs, 1st in Division/Conference/League, etc.)
- Calibration diagnostics (Brier decomposition, ECE, reliability diagrams, baseline comparisons)

---

## Dashboard Tabs

1. **Model Configuration**  
   Sport, season, adjustments, advanced initial-Elo controls, and optimized parameters from the last run.

2. **Season Simulation**  
   Monte Carlo regular-season simulations with expected wins/points, distributions, uncertainty ranges, and achievement probabilities.

3. **Elo Ratings**  
   Post-game Elo ratings with conference/division filtering and team colors.

4. **Elo Trajectory**  
   Historical Elo paths + simulated trajectories with uncertainty bands.

5. **Model Evaluation**  
   Accuracy, Log Loss, Brier Score, calibration plots, residual diagnostics, Log5 baseline, and grid-search landscape.

---

## Core Architecture (stable since v5)

The engine is the only component that orchestrates Elo execution. Everything else is configuration, reusable transformations, evaluation utilities, or workflow orchestration.

Public engine API:

```python
run_game(home_elo, away_elo, context, config)
```

Model behavior is controlled entirely through declarative configuration. Adjustments (Home Advantage, Margin of Victory, Elevation Edge) are implemented as stateless transformations in a pregame/postgame pipeline.

### Repository Structure

```
elo_lab/
├── engine/          # Execution engine (game lifecycle + orchestration)
├── adjustments/     # Stateless transformations
├── configuration/   # Model and sport configurations
├── evaluation/      # Metrics and diagnostics
└── workflows/       # Backtesting, simulation, optimization

app/
├── dashboard.py     # Streamlit entry point
├── metadata/        # Teams, venues, elevation data (NHL / NBA / NFL)
├── services/        # Simulation, evaluation, Elo evolution, etc.
└── tabs/            # Individual dashboard tab implementations
```

---

## Supported Sports

| Sport | Status          | Notes                                              |
|-------|-----------------|----------------------------------------------------|
| NHL   | Fully supported | Points system + OT handling, Home-Ice Advantage    |
| NBA   | Fully supported | Home-Court Advantage, multi-season data            |
| NFL   | Fully supported | Wins-based outcomes, Home-Field Advantage, proper playoff-qualification logic |

All sports share the same engine and dashboard. Sport-specific logic (scoring rules, home-advantage labels, achievement columns, team colors, venue elevations) is driven by configuration and metadata.

---

## Key Features in Detail

### Adjustments
- **Home Advantage** — configurable Elo boost (sport-specific labeling)
- **Margin of Victory** — scales the Elo update by score differential
- **Elevation Edge** — continuous: `elev_value × max(0, home_ft − away_ft) / 1000`

### Advanced Initial Elo Controls
- Rating source: previous-season playoffs or regular-season standings
- Rating basis: record or existing Elo
- Optional regression-to-mean with adjustable strength

### Parameter Optimization
Users can selectively optimize any subset of enabled adjustments. The system runs a grid search and surfaces the best combination via an interactive heatmap (Grid Search Landscape) plus a top-10 table.

### Evaluation & Diagnostics
- Accuracy / Log Loss / Brier Score
- Brier score decomposition (Reliability, Resolution, Uncertainty) + ECE
- Reliability diagrams
- Log5 baseline comparison
- Residual diagnostics
- Home-win-rate and coin-flip baselines with explicit lift columns

---

## Quick Start

```bash
git clone https://github.com/elevation-edge-sports-data/multisport-elo-lab.git
cd multisport-elo-lab
pip install -r requirements.txt
streamlit run app/dashboard.py
```

---

## Version History Summary

| Version | Focus |
|---------|-------|
| 5       | Canonical engine + declarative transformation pipeline |
| 6       | Interactive Streamlit dashboard |
| 7       | Parameter optimization + original Elevation Edge (binned) |
| 8.0–8.2 | Multi-sport (NHL) + achievement probabilities + calibration + NFL playoff-logic fix |
| 9       | Multiseason support + full NBA integration + advanced initial-Elo controls |
| 10      | Continuous Elevation Edge + Log5 baseline + residual diagnostics |

See [CHANGELOG.md](CHANGELOG.md) for the complete history.

---

## Notes

- This project is under active development.
- Season Simulation currently covers the **regular season only** (including probabilities of making the playoffs and finishing 1st in division/conference/league). Full playoff-bracket / series simulation is not yet implemented.
- Elevation data uses real stadium/arena elevations.

---

## License & Contact

Built by [Zach Sajevic](https://github.com/elevation-edge-sports-data)  
Sports Analytics Engineer | Predictive Modeling & Interactive Data Products
