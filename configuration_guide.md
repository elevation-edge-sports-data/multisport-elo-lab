# Configuration Guide

## Overview

Configuration defines **what model runs**, not how it runs.

It controls:

* Elo parameters
* adjustment activation
* adjustment parameters
* model variants

---

## Model Configuration Structure

```python
{
    "k": 20,

    "pregame_pipeline": [
        "home_field"
    ],

    "postgame_pipeline": [
        "margin_of_victory"
    ],

    "adjustments": {
        "home_field": {
            "enabled": True,
            "value": 55
        },
        "margin_of_victory": {
            "enabled": False,
            "scale": 1.0
        }
    }
}
```

---

## Key Fields

### k-factor

Controls Elo update sensitivity.

* higher → more reactive ratings
* lower → more stable ratings

---

### adjustments

Each adjustment has:

* `enabled` (bool)
* parameters specific to that adjustment

Example:

```python
"home_field": {
    "enabled": True,
    "value": 55
}
```

---

## Pipeline Interaction

Configuration drives:

* which transformations are active
* pregame and postgame execution order
* parameter values passed into transformations

---

## Rules

✔ configuration is declarative
✔ configuration contains no logic
✔ configuration defines model behavior through data rather than computation
