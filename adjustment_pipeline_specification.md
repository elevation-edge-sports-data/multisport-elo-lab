# Adjustment Pipeline Specification

## Design Goal

The adjustment pipeline is the execution layer for all model transformations inside the engine.

It guarantees:

* Composable transformations
* Deterministic execution
* Separation between orchestration and adjustment logic
* A shared state contract for every transformation

The pipeline is responsible only for executing transformations. It does not implement model behavior itself.

---

# Transformation Definition

A transformation is a pure function that accepts a canonical state object and returns the modified state.

```python
state -> state
```

Every transformation must:

* Operate only on the supplied state
* Return the modified state
* Avoid side effects
* Avoid orchestration logic

---

# Canonical State

Every transformation receives the same state object.

```python
state = {
    "home_elo": float,
    "away_elo": float,

    "context": {
        "home_team": str,
        "away_team": str,
        "season": int,
        "week": int,
        "home_score": int | None,
        "away_score": int | None,
        "actual": int | None,
    },

    "config": {
        "adjustments": {
            ...
        }
    },

    "postgame": {}
}
```

No transformation owns the state. Every transformation operates on the same shared object.

---

# Pregame Stage

Pregame transformations execute before win probability is calculated.

Examples include:

* Home-field advantage
* Travel adjustments
* Rest adjustments

Purpose:

* Modify Elo ratings prior to prediction.

---

# Postgame Stage

Postgame transformations execute after the game outcome is known but before Elo ratings are updated.

Examples include:

* Margin of victory

Purpose:

* Compute metadata consumed during the Elo update step.

Postgame transformations do not directly modify ratings.

---

# Pipeline Execution

The engine executes transformations sequentially.

```python
for transform in pregame:
    state = transform(state)

for transform in postgame:
    state = transform(state)
```

Execution order is deterministic and defined entirely by configuration.

---

# Pipeline Construction

Pipelines are built from the model configuration.

The pipeline builder:

* Reads enabled adjustments
* Resolves transformation modules
* Constructs ordered pregame and postgame execution lists

Transformation order is defined by the model configuration rather than the engine itself.

---

# Dynamic Transformation Loading

Transformations are imported dynamically.

```python
elo_lab.adjustments.<name>.apply
```

This allows new adjustments to be added without modifying engine execution code.

---

# Transformation Rules

Allowed:

* Read state
* Modify state
* Return state

Forbidden:

* Global state mutation
* Workflow execution
* Engine orchestration
* External side effects

Each transformation is responsible only for its own model behavior.

---

# Relationship to the Engine

The adjustment pipeline is executed through:

```python
elo_lab.engine.game_runner.run_game()
```

Workflows never invoke the pipeline directly.

All workflows execute games through `run_game()`, which delegates transformation execution to the pipeline.

---

# Design Guarantees

The pipeline guarantees:

* Deterministic execution
* Reproducible results
* Stateless transformations
* Configuration-driven execution
* Separation between execution and model behavior

---

# Architectural Role

The adjustment pipeline is responsible only for executing transformations.

* Individual adjustments define model behavior.
* The engine defines execution.
* The pipeline connects the two.

This separation allows new adjustments to be introduced without modifying the engine or existing workflows.
