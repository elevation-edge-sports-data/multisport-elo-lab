# Transformation Lifecycle

## Overview

A transformation is a stateless function that modifies game state.

All transformations follow the same lifecycle inside the pipeline.

---

## 1. Loading Phase

Transformations are loaded dynamically by the pipeline using Python's import system.

```python
elo_lab.adjustments.<name>.apply
```

This allows:

* modular design
* plug-and-play adjustments
* no engine modification required

---

## 2. Registration Phase

The pipeline builder:

* reads configuration
* checks `enabled` flags
* orders transformations

---

## 3. Pregame Execution

Executed before probability calculation:

```python
state = transform(state)
```

Used for:

* rating adjustments
* pregame contextual modifications

---

## 4. Postgame Execution

Executed immediately before the Elo rating update using the recorded game outcome:

Used for:

* margin-of-victory multipliers
* derived metadata

---

## 5. State Mutation Rules

Transformations:

✔ may modify `state`
✔ must return `state`
✔ must remain stateless externally

---

## 6. Execution Constraints

* deterministic order
* sequential execution only
* no parallel execution
* no side effects outside state

---

## 7. Lifecycle Summary

```
load → configure → execute pregame → compute probability → execute postgame → update Elo
```
