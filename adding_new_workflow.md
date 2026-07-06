# Adding a New Workflow

## Overview

A workflow is an end-to-end process built on top of the engine.

All workflows live in:

```
elo_lab/workflows/
```

---

## Step 1 — Define Purpose

Examples:

* backtesting
* simulation
* optimization
* evaluation

---

## Step 2 — Import Engine Only

All workflows must use:

```python
from elo_lab.engine.game_runner import run_game
```

Most workflows interact with the engine exclusively through `run_game()`. Supporting utilities (such as shared constants) may be imported when appropriate.

---

## Step 3 — Load Data

Workflows are responsible for preparing inputs to the engine. Typical tasks include:

* reading data files
* iterating schedules
* managing simulations

---

## Step 4 — Call Engine

```python
result = run_game(
    home_elo,
    away_elo,
    context,
    config
)
```

---

## Step 5 — Aggregate Results

Workflows may:

* store outputs
* compute statistics
* write files

---

## Rules

❌ Do NOT implement Elo logic
❌ Do NOT perform Elo calculations directly
❌ Do NOT replicate pipeline logic

✔ Only orchestrate engine execution

---

## Design Principle

> Workflows prepare data, coordinate execution, and collect results. The engine performs all game-level Elo calculations.
