# Adding a New Transformation

## Overview

A transformation is a stateless function that modifies Elo state.

All transformations live in:

```
elo_lab/adjustments/
```

---

## Step 1 — Create File

Example:

```
elo_lab/adjustments/travel.py
```

---

## Step 2 — Implement `apply(state)`

```python
def apply(state):
    config = state["config"]["adjustments"]["travel"]

    if not config.get("enabled", False):
        return state

    # modify state
    state["home_elo"] -= config.get("penalty", 0)

    return state
```

---

## Step 3 — Add Configuration

In `configuration/model_configs.py`, add the adjustment to the model's `adjustments` dictionary:

```python
"travel": {
    "enabled": True,
    "penalty": 5
}
```

---

## Step 4 — Pipeline Integration

No engine changes required.

The pipeline automatically loads:

```python
elo_labadjustments.travel.apply
```

---

## Rules

✔ must be stateless
✔ must accept and return state
✔ must not call engine functions
✔ must not perform orchestration

---

## Design Benefit

Adding a new transformation typically requires:

* creating one adjustment module
* adding its configuration parameters
* registering it in the appropriate pipeline

No engine or workflow changes are required.
