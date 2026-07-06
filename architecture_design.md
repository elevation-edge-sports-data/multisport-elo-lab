# Elo Lab Architecture

## Design Philosophy

Elo Lab is structured around a single principle:

> **The engine is the only source of truth for model execution.**

All other components either:
- define configuration
- define transformations
- orchestrate workflows
- evaluate outputs

The system is divided into four core layers:

1. configuration (what to run)
2. adjustments (how ratings are modified)
3. engine (how games are executed)
4. workflows (how experiments are run)

---

# Core Execution Flow

All simulations and backtests follow this pipeline:

workflow
→ engine.run_game()
→ build state
→ apply adjustments
→ compute win probability
→ determine game outcome
→ update Elo
→ return result

The engine is the **single orchestrator of all game-level logic**.

---

# engine/

## Purpose

The engine implements the complete game execution lifecycle.

It is responsible for:

- constructing canonical game state
- executing the configured transformation pipeline
- computing win probabilities
- applying Elo updates
- returning standardized results

## Key Components

- `game_runner.py` → main entry point (`run_game`)
- `pipeline.py` → transformation orchestration system
- `probability.py` → Elo win probability model
- `updates.py` → Elo rating update logic
- `state_schema.py` → canonical state definition
- `state_validator.py` → validation layer
- `constants.py` → shared constants

## Rules

- Engine MUST NOT contain workflow logic.
- Engine MUST NOT contain evaluation logic.
- Engine MAY import adjustments.
- Engine MUST remain sport-agnostic.

---

# adjustments/

## Purpose

Adjustments are stateless transformation functions that modify Elo state.

Each adjustment:

- is a pure function
- operates on a shared state object
- is enabled or disabled through configuration
- does not perform orchestration

Current adjustments include:

- home_field
- margin_of_victory

## Rules

- One file = one transformation
- No orchestration logic
- No pipeline logic
- No workflow dependencies

---

# configuration/

## Purpose

Defines model behavior through declarative settings.

Configuration specifies:

- enabled adjustments
- adjustment parameters
- model variants
- sport defaults

Configuration defines model structure and parameter values. It contains no executable model logic.

---

# evaluation/

## Purpose

Evaluation measures model performance.

Examples include:

- accuracy
- log loss
- Brier score
- diagnostics
- model comparison

Evaluation consumes model outputs but never modifies model behavior.

---

# workflows/

## Purpose

Workflows execute complete analytical processes.

Current workflows include:

- historical backtesting
- season simulation
- parameter optimization
- model evaluation

Workflows coordinate execution but contain no Elo implementation.

All game execution is delegated to `engine.run_game()`.

---

# Dependency Rules

Dependency flow is strictly one-directional.

workflows
→ configuration
→ engine
→ adjustments

evaluation
← workflows

Forbidden dependencies:

- engine → workflows
- adjustments → workflow orchestration
- adjustments → pipeline construction
- evaluation → engine mutation

---

# Architectural Principle

Every module should have exactly one responsibility.

If a module begins serving multiple responsibilities, it should be split rather than expanded.

This keeps the framework maintainable, testable, and extensible.