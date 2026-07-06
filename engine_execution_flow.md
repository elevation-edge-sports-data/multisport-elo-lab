# Engine Execution Flow

## Overview

All game-level computation in Elo Lab is executed through:

```
elo_lab.engine.game_runner.run_game()
```

This is the single entry point for:

* state construction
* adjustment execution
* probability computation
* Elo update
* result packaging

---

## Step-by-Step Execution

### 1. Input State Construction

The engine receives:

```python
home_elo: float
away_elo: float
context: dict
config: dict
```

This is assembled into:

```python
state = {
    "home_elo": float,
    "away_elo": float,
    "context": {...},
    "config": {...},
    "postgame": {}
}
```

---

### 2. Adjustment Pipeline Execution

The engine calls:

```
elo_lab.engine.pipeline.apply_adjustments()
```

This executes:

#### Pregame transformations

* Modify ratings before probability calculation

#### Postgame transformations

* Compute metadata used for Elo update

All transformations are:

* stateless
* configuration-driven
* executed sequentially

---

### 3. Win Probability Calculation

After pregame adjustments:

```python
p_home = win_probability(home_elo, away_elo)
```

This is computed using the Elo model in:

```
engine/probability.py
```

---

### 4. Outcome Determination

The engine determines the game outcome using either:

```python
context["actual"]
```

or, if `actual` is not provided,

```python
context["home_score"]
context["away_score"]
```

In the latter case, the game outcome is inferred from the final score.

---

### 5. Elo Update

The update step:

```python
update_elo(
    home_elo,
    away_elo,
    actual,
    p_home,
    k=config["k"],
    multiplier=state["postgame"].get("mov_multiplier", 1.0)
)
```

Defined in:

```
engine/updates.py
```

---

### 6. Output

The engine returns:

```python
{
    "home_elo_pre": float,
    "away_elo_pre": float,
    "home_elo_adjusted": float,
    "away_elo_adjusted": float,
    "p_home": float,
    "actual": int,
    "multiplier": float,
    "home_elo_post": float,
    "away_elo_post": float,
}
```

---

## Key Property

> The engine fully owns execution. Workflows never implement logic.
