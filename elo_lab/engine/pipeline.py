"""
Transformation pipeline.

Builds and executes the configured sequence of pregame and
postgame Elo model transformations.
"""

from importlib import import_module
from typing import Any, Dict, List


# ==========================================================
# PIPELINE EXECUTION
# ==========================================================

def run_pipeline(
    state: Dict[str, Any],
    pregame_transforms: List,
    postgame_transforms: List,
) -> Dict[str, Any]:
    """
    Executes the configured pregame and postgame transformation
    pipeline for a canonical engine state.
    """

    state = dict(state)

    for transform in pregame_transforms:
        state = transform(state)

    state["postgame"] = dict(state.get("postgame", {}))

    for transform in postgame_transforms:
        state = transform(state)

    return state


# ==========================================================
# TRANSFORMATION LOADER
# ==========================================================

def load_transformation(name: str):
    """
    Dynamically imports a transformation from the adjustments
    package.
    """

    module = import_module(f"elo_lab.adjustments.{name}")

    return module.apply


# ==========================================================
# PIPELINE BUILDER
# ==========================================================

def build_pipeline(config: Dict[str, Any]):
    """
    Builds the enabled pregame and postgame transformation
    pipelines from a model configuration.
    """

    adjustments = config.get("adjustments", {})

    pregame: List = []
    postgame: List = []

    for name in config.get("pregame_pipeline", []):
        adjustment = adjustments.get(name, {})
        if adjustment.get("enabled", False):
            pregame.append(load_transformation(name))

    for name in config.get("postgame_pipeline", []):
        adjustment = adjustments.get(name, {})
        if adjustment.get("enabled", False):
            postgame.append(load_transformation(name))

    return pregame, postgame


# ==========================================================
# ENTRY POINT
# ==========================================================

def apply_adjustments(
    home_elo: float,
    away_elo: float,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Constructs the canonical engine state and executes the
    configured transformation pipeline.
    """

    state = {
        "home_elo": float(home_elo),
        "away_elo": float(away_elo),
        "context": dict(context),
        "config": config,
        "postgame": {},
    }

    pregame, postgame = build_pipeline(config)

    return run_pipeline(state, pregame, postgame)