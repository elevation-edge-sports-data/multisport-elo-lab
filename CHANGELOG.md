# Changelog

## Version 8.2 — NFL Achievement Probabilities Fix

### Fixed
- **NFL Season Simulation tab** no longer displays the NHL-only "Home Ice (Top 2 in Div)" column
- NFL achievement table now shows exactly four probabilities: Make Playoffs, 1st in Division, 1st in Conference, 1st in League
- NFL achievement probabilities were previously a placeholder (only "Make Playoffs" was non-zero)
- Implemented proper NFL playoff structure: 4 division winners + 3 wild cards per conference
- All four probability columns now produce realistic, non-zero values from Monte Carlo simulations

### Improved
- Achievement probability calculation is now fully multi-sport aware (NHL, NFL logic paths)
- Season Simulation display logic is sport-conditional


## Version 8.1 — Calibration, Brier Decomposition & Grid Search Landscape

### Added
- **Brier score decomposition** on the Model Evaluation tab
  - Reliability, Resolution, and Uncertainty components
  - Expected Calibration Error (ECE) as a single-number summary
- **Calibration plot** (reliability diagram)
  - Binned predicted win probability vs observed win rate
  - Perfect-calibration diagonal and sample-size-aware markers
- **Baseline comparisons**
  - Home Win Rate and Coin Flip (0.5) baselines shown alongside the selected model
  - Explicit delta columns quantifying lift over the naïve baselines
- **Grid Search Landscape** visualization
  - Interactive heatmap of any two optimized parameters
  - Metric selector (Log Loss / Brier / Accuracy)
  - Clear marker for the best combination
  - Top-10 parameter combinations table
- Extended evaluation service now provides access to raw prediction arrays for calibration and decomposition calculations

### Improved
- Model Evaluation tab now surfaces deeper diagnostics on calibration, resolution, and optimization results
- Users can inspect any backtested model individually via a selector

## Version 8.0 — Multisport NHL Integration + Achievement Probabilities

### Added

* Full multi-sport support with NHL integrated alongside NFL
* Complete NHL team metadata (`app/metadata/nhl_teams.py`) including conference, division, and primary/secondary colors for all 32 teams
* NHL schedule/game data (`data/nhl_games.csv`)
* Sport selector in the dashboard sidebar (NHL / NFL, defaults to NHL)
* **Regular Season Achievement Probabilities** derived from Monte Carlo simulations:
  * Make Playoffs
  * Home Ice (Top 2 in Division)
  * 1st in Division
  * 1st in Conference
  * 1st in League
* Sport-specific simulation logic (NHL points system + overtime handling vs NFL win-based outcomes)
* Dynamic metric handling in the Season Simulation tab (points for NHL, wins for NFL)
* Team-colored visualizations that pull from the selected sport’s branding

### Changed

* Dashboard, simulation service, and all major tabs (Season Simulation, Elo Ratings, Elo Evolution, Model Evaluation) are now fully multi-sport aware
* Season simulation workflow generalized via sport configuration (schedule path, scoring rules, OT rate, etc.)
* Schedule loading, initial Elo ratings, conference/division filters, and team lookups are now sport-dependent
* Achievement probability table is sorted by Make Playoffs probability and displayed with clean, user-friendly column names

### Improved

* Simulation results now surface high-value outcome probabilities beyond just win/point totals
* Visual consistency across sports through proper team colors
* Expanded suite of backtest outputs across many parameter combinations (MOV, HFA, k-factor, etc.)

## Version 7.0 — Parameter Optimization & Elevation Edge

### Added
- Full implementation of **Elevation Edge** adjustment (signature feature)
  - Binning system to avoid overfitting to raw elevation values
  - Home-team elevation advantage based on bin difference
  - Integrated into configuration system and parameter optimization
- Generalized parameter optimization system
  - Users can now select any subset of active adjustments to optimize
  - `optimize_parameters_for_config()` supports dynamic grids per adjustment
- Improved runtime feedback
  - Replaced static runtime estimates with `st.status()` + progress bar in sidebar
  - Clearer messaging during optimization and simulation phases

### Changed
- Adjustment checkboxes are now fully wired and functional
- `build_model_config()` properly includes `elevation_edge` when enabled
- Optimization grid now includes `elevation_edge` parameter
- Default simulation count changed from 1000 → 100
- Added Broncos orange theming for checkboxes and progress bars
- Model Configuration tab now shows optimized parameters when used
- Season Simulation and Elo Evolution tabs now display active configuration context

### Improved
- Overall dashboard UX during long-running simulations (especially with optimization enabled)
- Visibility into which model configuration produced the displayed results

## Version 6.0 — Interactive Streamlit Dashboard

### Added
- Streamlit dashboard application layer built on top of the existing Elo Lab engine
- Interactive dashboard tabs for:
  - Model configuration summaries
  - Monte Carlo season simulation
  - Elo rating visualization
  - Historical and simulated Elo evolution
  - Model evaluation and comparison
- Interactive exploration of Monte Carlo simulation outputs, including:
  - Expected win summaries
  - Team win distributions
  - Simulation uncertainty ranges
- Historical Elo visualization tools, including:
  - Current team Elo rankings
  - Conference and division filtering
  - Team Elo evolution over time
- Simulated Elo evolution visualization with uncertainty bands from Monte Carlo simulations

### Changed
- Added a user-facing analytics layer for exploring outputs generated by existing Elo workflows
- Integrated dashboard services for simulation, backtesting, Elo evolution, and model evaluation workflows

### Notes
- Version 6 extends the existing Elo Lab engine architecture without replacing the underlying modeling workflows.
- Dashboard controls currently support simulation execution and output exploration; full interactive model parameter configuration is planned for a future version.

## Version 5.0 — Engine Refactor

### Added
- Canonical engine package (`elo_lab/engine`)
- Unified `run_game()` execution API
- Configuration-driven transformation pipeline
- Stateless adjustment framework
- Sport configuration system
- Canonical state schema and validation layer

### Changed
- Refactored all workflows to use engine API exclusively
- Eliminated duplicated Elo logic across workflows
- Replaced procedural adjustment logic with declarative pipeline

### Removed
- Legacy adjustment pipeline (`adjustments/pipeline.py`)
- Legacy core adjustment logic (`adjustments/core.py`)

### Notes
- Game outcomes may be provided either through `context["actual"]` or inferred from `home_score` and `away_score`.
- All game execution is routed through the canonical `run_game()` engine API.