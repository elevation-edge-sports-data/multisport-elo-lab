# Changelog

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