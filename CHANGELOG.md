# Changelog

All notable changes to MultiSport Elo Lab are documented in this file.

## Version 13.0 — Playoff odds table, sortable playoff spirals, playoff path bars

### Added
- **Playoff Odds table** (Playoff Projections tab), styled after MoneyPuck’s predictions table:
  - Team column shows logo + abbreviation
  - Round probabilities with blue intensity shading alongside the numeric %
  - Projected wins / points and regular-season achievement columns when available
  - **Sortable** via Sort table by / Ascending controls on the main table
- **Playoff spirals** (one per conference: Eastern/Western or AFC/NFC):
  - **Radial metric** dropdown selects which round probability sets bar length
  - Conference leader on the selected metric fills the full radius
  - Wedge color = team primary; logos on wedges; hover shows the full playoff path
- **Playoff path bars** with fixed Color 1…5 palette (championship → make playoffs)
- Attribution captions for the odds table linking to [MoneyPuck](https://moneypuck.com/predictions.htm); numbers from this project’s Elo + Monte Carlo engine

### Changed
- Playoff Projections tab leads with the odds table, dual-conference spirals, and path bars
- Removed the single-team Quick Stats block from the Playoff Projections tab

---

## Version 12.3 — Numerical simulation progress bar; faster simulation; cleanup

### Added
- **Numerical progress bar**: while simulations run, the existing progress bar now reports at **10% increments** (0%, 10%, …, 100%) with an explicit numeric indicator next to “Running Monte Carlo simulations…”
- `progress_callback` support threaded through `simulate_many_seasons`, `simulate_many_seasons_multiyear`, the playoff wrapper, and `run_simulation`
- `return_season_results` flag on the primary Monte Carlo paths so per-sim `(standings_df, team_elo)` can be collected for playoffs

### Fixed
- **Faster simulation**: removed the redundant full regular-season loop previously used only to feed playoff seeding.
  - Primary Monte Carlo now optionally returns the per-sim standings + final Elo.
  - Playoff probabilities are accumulated from those same outcomes via the existing `accumulate_from_many_seasons` helpers (NFL / NHL / NBA).
  - Multiyear (target-season) path no longer triggers a second schedule load + full MC just for playoffs.
  - Typical runs do roughly half the previous Monte Carlo work (one pass instead of two).

### Changed
- Progress reporting during Run Simulation is continuous across regular-season (~0–85%) and playoff accumulation (~85–100%)
- Playoff home advantage is taken from the active model config when present

### Removed
- Unused tab modules that no longer correspond to active dashboard tabs: `app/tabs/configuration.py`, `app/tabs/elo_ratings.py`

---

## Version 12.2 — Match default sim settings to precomputed defaults; seed; logos in Playoff Outlook

### Added
- Team logos in the **Playoff Outlook** Team column (logo-only; no abbreviation)
- Regular Season Projections default team selection scoped to **Western** (NHL/NBA) or **AFC** (NFL)
- Sport-specific public defaults: NHL k=12 / home-ice 35, NBA k=22 / home-court 55, NFL k=20 / home-field 55
- Mild record-based prior before warm-up in the default-sim generator

### Changed
- Match sidebar / default-sim settings to the precomputed defaults
- Inter-season regression default **0.35**
- NBA default **Simulate from** set to **2024** (two-season warm-up before target 2026)
- Precomputed defaults regenerated with the new parameters and seed 42
- Sidebar k / home-advantage slider defaults follow the sport-specific public config
- Dashboard caption and module docstring set to **Version 12.2**

### Fixed
- v12.1 added a Random seed control in the sidebar (and the default-sim generator) and passed `seed=...` into `run_simulation`, but `run_simulation` did not accept a `seed` argument.
  - Fix: add `seed: int = 42` (and `inter_season_regression`) to `run_simulation`, and pass `seed` through to both `simulate_many_seasons_multiyear` and the playoff-aware `simulate_many_seasons` call.

### Removed
- **Championship contenders** panel (logo strip above the championship probability chart)

---

## Version 12.1 — Regular season trajectories, param eval, reproducibility

### Added
- **Regular Season Projections redesign**
  - Two-chart layout: **Observed** (prior completed season) above **Simulated** (target season)
  - Metric toggle: wins (NFL/NBA) or points (NHL), or standings rank
  - Default **Select teams** = top 6 by first-round / wild-card probability (NBA skips play-in when possible)
  - Multiselect refreshes when simulation results change
- **Cumulative wins/points** in simulation history so projected trajectories carry uncertainty bands
- **Historical parameter evaluation** on Run Simulation: one walk of the last completed season with current params → accuracy, log loss, Brier on Model Comparison (explicitly labeled as historical, not the upcoming slate)
- **Random seed** control in the sidebar (default 42); same seed + settings reproduces Monte Carlo draws
- **Simulation count** option **25** (100 remains default)
- Upcoming **NFL schedule** schemas: `VisTm` / `HomeTm`, Away/Home without scores yet
- Default-sim generator: sport-specific **Simulate from** (NHL 2025, NFL 2024, NBA 2025) and `--seed`

### Changed
- Sidebar **Adjustments** renamed **Parameters**
- **Simulate from** defaults: NHL 2025, NFL 2024, NBA 2025 (when available)
- Precomputed default load stamps season / simulate from / fingerprint so the UI matches the pickle
- Model Comparison Brier caption is the decomposition equation only (Reliability / Resolution / ECE explained on the metrics themselves)
- Version string **12.1**

### Fixed
- `generate_default_sims` import path when run as `python -m elo_lab.workflows.generate_default_sims`
- NFL 2026 schedule normalize failure (`FileNotFoundError` on target 2026) for upcoming PFR-style columns
- Regular Season Projections stuck on the same six teams after a new run (Streamlit multiselect key)

### Notes
- Regenerate precomputed pickles after this release so defaults include win trajectories and from_season alignment:
  `python -m elo_lab.workflows.generate_default_sims --n-sims 250 --seed 42`

---

## Version 12.0 — Simulate upcoming season

### Added
- **Simulate upcoming season** for **NFL 2026** and **NHL 2026–27**
  - Full regular-season slate + playoff bracket Monte Carlo for seasons that have not yet been played
  - Elo is warmed from actual prior seasons, then the upcoming target season is simulated
  - **NBA — coming soon** (after official schedule is released)
- **Simulate from** sidebar control: explicit start season for the Elo warm-up window (default = earliest valid season; seed year excluded)
- **Three-tab dashboard structure**
  - **Playoff Projections** (default landing) — former Season Simulation
  - **Regular Season Projections** — former Elo Trajectory
  - **Model Comparison** — former Model Evaluation
- **Expanded baselines** in Model Comparison:
  - **Always Home** — hard home prediction every game
  - **Constant Home Rate** — empirical home-win frequency as probability
  - **Coin Flip (p=0.5)** — uninformed baseline with theoretical accuracy 0.5
- **Export Results (.xlsx)** control: multi-sheet workbook available whenever simulation results exist

### Changed
- Dropped **Model Configuration** and **Elo Ratings** tabs
- **Margin of Victory** is pure binary (on = margin-scaled update; off = win/loss only); continuous scale slider removed
- **Apply regression to mean** moved into main Adjustments section and defaults to **True**
- Regression strength range expanded to **0.0–1.0**
- Initial Elo controls removed from the UI (rating source fixed to playoffs; rating basis prefers Elo with record fallback)
- "Optimize parameters" renamed **Grid Search**; expander renamed **Customize Parameters**
- Dashboard caption and version string updated to Version 12.0 — Simulate upcoming season

### Improved
- **Model configuration panel** hierarchy: Grid Search master checkbox with indented parameter targets only when enabled
- Baseline comparison caption explains why Always Home and Constant Home Rate can share accuracy while log loss / Brier differ
- Tooltips updated for clarity:
  - **k-factor**: plain-English explanation of reactive vs stable ratings
  - **Margin of Victory**: on = scaled by score differential; off = win/loss only
  - **Simulate from**: first season included in the warm-up window
  - **Apply regression to mean**: pull toward league mean after ranking / between seasons
  - **Regression strength**: how strongly ratings are pulled toward the mean
  - **Elevation Edge**: formula retained in help text (label no longer repeats units inline)

### Notes
- Regular Season Projections still shows rating trajectories; standings / win-total trajectory redesign is planned for a follow-up
- Playoff Projections is placed first in the tab bar so Streamlit opens it as the default landing view

---

## Version 11.5 — Warm-up Elo from recent actual seasons

### Added
- **Historical warm-up before target-season Monte Carlo**: prior releases started each simulation from a static / ranking-based prior and Monte Carlo'd only the selected season. v11.5 first updates Elo from **actual** regular-season and playoff results in the most recent completed seasons, then Monte Carlo runs only on the target season.
- Playoff games in the warm-up use a higher K (k×1.75) so deep runs and early exits move ratings more than regular-season games.
- Stronger inter-season regression toward the mean after each warm-up season.
- Season dropdown lists only **simulatable** targets (earliest data year is reserved for history, not offered as a simulation target).

### Changed
- Default simulations and Run Simulation use the warm-up path by default.
- Season Simulation playoff outlook table ordered by Reach Wild Card (NFL) or Reach First Round (NHL/NBA).

### Notes
- Rankings on first open should better reflect recent real results than a single-year prior alone; history window and regression strength remain open to tuning in later releases.

---

## Version 11.4 — Team Logos

### Added
- **Team logos** across the dashboard
  - Sport-specific assets under `app/assets/logos/{nhl,nfl,nba}/`
  - Logos in Elo Ratings, Elo Trajectory, and Season Simulation views
  - Shared logo helpers in `app/components/logos.py` and metadata resolution
- Logo strip for playoff / championship contenders on the Season Simulation tab

### Changed
- Logo layout reorganized from a flat folder into per-sport subfolders
---


## Version 11.3 — Full Results Export

### Added
- **One-click full results export** (multi-sheet Excel)
  - Global **Download Full Results (.xlsx)** button appears as soon as simulation results exist (defaults or custom runs)
  - Single file contains:
    - Config (model parameters + run metadata)
    - Simulation Summary
    - Achievement + Playoff probabilities
    - Elo Ratings
    - Evaluation metrics (when available)
- New `app/services/export_service.py`
  - Builds the workbook from current `st.session_state`
  - Gracefully omits sheets that have no data

### Improved
- Export button is placed after default results are loaded, so it appears on first visit
- Export failures are caught and shown as a warning — they never break the rest of the dashboard

## Version 11.2 — Instant Default Simulations

### Added
- **Precomputed default simulations** load automatically when switching sports  
  - No 20-second wait to see baseline results  
  - Override anytime with **Run Simulation**
- `elo_lab/workflows/generate_default_sims.py`  
  - One-command generator for NHL / NBA / NFL defaults  
  - `python -m elo_lab.workflows.generate_default_sims`
- 1000-sim model comparison baseline under `outputs/`

### Changed
- `.gitignore` expanded for precomputed pickles and common artifacts

### Improved
- Season Simulation tab shows a clear caption when displaying defaults

---

## Version 11.1 — NHL + NBA Playoff Brackets

### Added
- Full **NHL** playoff simulation  
  - Top-3 per division + 2 wild cards  
  - Fixed bracket, best-of-7 series (2-2-1-1-1) through Stanley Cup
- Full **NBA** playoff simulation  
  - Play-In tournament (7–10)  
  - Fixed 1–8 bracket, best-of-7 series through NBA Finals
- Multi-sport dispatch in `simulate_with_playoffs.py`
- Playoff outlook table + championship probability chart for all three sports

### Changed
- Season Simulation tab generalized for sport-specific round names and labels
---


## Version 11.0 — NFL Playoff Simulation

### Added
- Full **NFL** playoff-bracket simulation  
  - 4 division winners + 3 wild cards per conference  
  - Wild Card → Divisional → Conference → Super Bowl with reseeding  
  - Single-elimination games driven by final regular-season Elo + home advantage
- `elo_lab/playoffs/nfl/` package (models, seeding, simulation, adapter, workflow hook)
- Playoff outlook probabilities in the Season Simulation tab (NFL)

---

## Version 10 — Log5 Baseline, Residual Diagnostics & Continuous Elevation Edge

### Added
- **Log5 baseline** predictions and full calibration reports for direct comparison against Elo models
- Residual diagnostics in the Model Evaluation tab
- **Continuous Elevation Edge**: Elo points awarded per 1,000 ft of altitude difference  
  - Slider range 0.0–10.0 (default 1.0, step 0.5)  
  - Formula: `elev_value × max(0, home_ft − away_ft) / 1000`  
  - Optimization searches discrete values [0, 2, 4, 6, 8, 10]
- Sport-specific home-advantage UI labels  
  - NHL → Home-Ice Advantage  
  - NBA → Home-Court Advantage  
  - NFL → Home-Field Advantage

### Changed
- Elevation Edge moved from discrete bins to continuous altitude differential
- Default elevation value set to 1.0

### Improved
- Clearer residual and baseline comparisons in evaluation views
- Consistent sport ordering (**NHL · NBA · NFL**) across the entire application

---

## Version 9 — Multiseason + NBA + Advanced Parameters

### Added
- Full **NBA** support  
  - Team metadata, venue elevations, schedule data  
  - Home-Court Advantage labeling and logic
- Multi-season schedule loading and dynamic season selector for NHL, NBA, and NFL
- Advanced initial-Elo controls (under “Advanced parameters” expander):  
  - `rating_source`: `"playoffs"` (default) or `"regular_season"`  
  - `rating_basis`: `"record"` or `"elo"`  
  - `apply_regression` checkbox + `regression_strength` slider (0.0–0.75)
- Explicit engine parameter sliders:  
  - k-factor (5–40, default 20)  
  - Home advantage value (0–100, default 55)  
  - Margin-of-victory scale (0.0–3.0, default 1.0)  
  - Elevation Edge value

### Changed
- Sport selector order standardized to **NHL · NBA · NFL**
- Initial ratings service now season-aware and regression-capable
- Simulation, Elo Ratings, and Elo Trajectory tabs fully multi-season aware
- `build_model_config()` accepts explicit parameter values

### Improved
- Session state now tracks season, rating source/basis, and regression settings for downstream tabs

---

## Version 8.2 — NFL Achievement Probabilities Fix

### Fixed
- NFL Season Simulation tab no longer displays the NHL-only “Home Ice (Top 2 in Div)” column
- NFL achievement table now shows exactly four probabilities:  
  Make Playoffs · 1st in Division · 1st in Conference · 1st in League
- Implemented proper NFL playoff qualification logic (4 division winners + 3 wild cards per conference)
- Achievement probability calculations are now fully multi-sport aware and produce realistic non-zero values

---

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

---

## Version 8.0 — Multisport NHL Integration + Achievement Probabilities

### Added
- Full multi-sport support with NHL integrated alongside NFL
- Complete NHL team metadata (`app/metadata/nhl_teams.py`) including conference, division, and primary/secondary colors for all 32 teams
- NHL schedule/game data (`data/nhl_games.csv`)
- Sport selector in the dashboard sidebar (NHL / NFL, defaults to NHL)
- **Regular Season Achievement Probabilities** derived from Monte Carlo simulations:  
  - Make Playoffs  
  - Home Ice (Top 2 in Division)  
  - 1st in Division  
  - 1st in Conference  
  - 1st in League
- Sport-specific simulation logic (NHL points system + overtime handling vs NFL win-based outcomes)
- Dynamic metric handling in the Season Simulation tab (points for NHL, wins for NFL)
- Team-colored visualizations that pull from the selected sport’s branding

### Changed
- Dashboard, simulation service, and all major tabs (Season Simulation, Elo Ratings, Elo Evolution, Model Evaluation) are now fully multi-sport aware
- Season simulation workflow generalized via sport configuration (schedule path, scoring rules, OT rate, etc.)
- Schedule loading, initial Elo ratings, conference/division filters, and team lookups are now sport-dependent
- Achievement probability table is sorted by Make Playoffs probability and displayed with clean, user-friendly column names

### Improved
- Simulation results now surface high-value outcome probabilities beyond just win/point totals
- Visual consistency across sports through proper team colors
- Expanded suite of backtest outputs across many parameter combinations (MOV, HFA, k-factor, etc.)

---

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

---

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

---

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

