# Elo Lab — Version 5

## Overview

Elo Lab is a modular, configuration-driven Elo rating and simulation framework designed for:

- Sports modeling
- Historical backtesting
- Monte Carlo simulation
- Parameter optimization
- Transformation-based rating systems

Version 5 introduces a complete architectural refactor centered around a single execution engine, declarative model configuration, and a stateless transformation pipeline.

The result is a framework in which every workflow shares the same execution path while model behavior is controlled entirely through configuration.

---

## Architecture

### Core Principle

> The engine is the only component that orchestrates Elo execution.

Everything else is either configuration, reusable transformations, evaluation utilities, or workflow orchestration.

---

## Public Engine API

All workflows execute games through a single public interface:

```python
run_game(home_elo, away_elo, context, config)
```

### Responsibilities

The engine is responsible for:

1. Constructing the canonical game state
2. Executing the pregame transformation pipeline
3. Computing win probability
4. Executing the postgame transformation pipeline
5. Updating Elo ratings
6. Returning a standardized result object

No workflow implements Elo logic directly.

---

## Repository Structure

```text
elo_lab/
├── engine/          # Execution engine (game lifecycle + orchestration)
├── adjustments/     # Stateless transformations
├── configuration/   # Model and sport configurations
├── evaluation/      # Metrics and diagnostics
└── workflows/       # Backtesting, simulation, optimization
```

---

## Version 5 Design Improvements

### Single Engine Orchestrator

All game execution flows through a single function:

```python
engine.game_runner.run_game()
```

This eliminates duplicated Elo logic across workflows.

---

### Declarative Model Configuration

Model behavior is controlled entirely through configuration.

Example:

```json
"adjustments": {
    "home_field": {
        "enabled": true,
        "value": 55
    },
    "margin_of_victory": {
        "enabled": false,
        "scale": 1.0
    }
}
```

The engine consumes configuration without requiring workflow-specific logic.

---

### Stateless Transformations

Each adjustment is implemented as an independent transformation.

Every transformation is:

- Stateless
- Deterministic
- Independently testable
- Pipeline-executed
- Configuration-driven

The engine orchestrates execution; transformations contain the model behavior.

---

### Thin Workflow Layer

Workflows no longer implement Elo calculations.

Instead they only:

- Load data
- Prepare inputs
- Call `run_game()`
- Aggregate outputs
- Save or analyze results

This architecture ensures that every workflow shares the exact same Elo implementation.

---

## Version 5 Milestones

Version 5 completes the architectural framework by introducing:

- Unified `run_game()` execution interface
- Declarative transformation pipeline
- Configuration-driven models
- Separation of engine and workflows
- Modular repository organization
- Reusable workflow architecture
- Stable public engine API

---

## Future Work

Version 6 will build on the Version 5 architecture by focusing on capabilities rather than structure.

Planned improvements include:

- Prediction mode (supporting games without known outcomes)
- Removal of the temporary `actual` context requirement
- Expanded sport abstraction
- Additional transformations
- Real-time inference workflows
- New simulation and forecasting capabilities