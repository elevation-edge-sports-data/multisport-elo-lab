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

def run_pregame_pipeline(
    state: Dict[str, Any],
    pregame_transforms: List,
) -> Dict[str, Any]:
    """
    Executes only pregame transformations.

    Used for deterministic pregame probability calculations.
    """

    state = dict(state)

    for transform in pregame_transforms:
        state = transform(state)

    return state


def run_postgame_pipeline(
    state: Dict[str, Any],
    postgame_transforms: List,
) -> Dict[str, Any]:
    """
    Executes only postgame transformations.

    Used after game outcome is known.
    """

    state = dict(state)

    state["postgame"] = dict(
        state.get("postgame", {})
    )

    for transform in postgame_transforms:
        state = transform(state)

    return state


def run_pipeline(
    state: Dict[str, Any],
    pregame_transforms: List,
    postgame_transforms: List,
) -> Dict[str, Any]:
    """
    Executes complete transformation pipeline.

    Maintained for backward compatibility.
    """

    state = run_pregame_pipeline(
        state,
        pregame_transforms,
    )

    state = run_postgame_pipeline(
        state,
        postgame_transforms,
    )

    return state


# ==========================================================
# TRANSFORMATION LOADER
# ==========================================================

def load_transformation(name: str):
    """
    Dynamically imports a transformation from the adjustments
    package.
    """

    module = import_module(
        f"elo_lab.adjustments.{name}"
    )

    return module.apply


# ==========================================================
# PIPELINE BUILDER
# ==========================================================

def build_pipeline(config: Dict[str, Any]):
    """
    Builds enabled pregame and postgame pipelines.
    """

    adjustments = config.get(
        "adjustments",
        {},
    )

    pregame = []
    postgame = []

    for name in config.get(
        "pregame_pipeline",
        [],
    ):
        adjustment = adjustments.get(
            name,
            {},
        )

        if adjustment.get(
            "enabled",
            False,
        ):
            pregame.append(
                load_transformation(name)
            )

    for name in config.get(
        "postgame_pipeline",
        [],
    ):
        adjustment = adjustments.get(
            name,
            {},
        )

        if adjustment.get(
            "enabled",
            False,
        ):
            postgame.append(
                load_transformation(name)
            )

    return pregame, postgame


# ==========================================================
# BACKWARD COMPATIBILITY ENTRY POINT
# ==========================================================

def apply_adjustments(
    home_elo: float,
    away_elo: float,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executes the complete transformation pipeline.

    Existing workflows may continue using this function.
    """

    state = {
        "home_elo": float(home_elo),
        "away_elo": float(away_elo),
        "context": dict(context),
        "config": config,
        "postgame": {},
    }

    pregame, postgame = build_pipeline(config)

    return run_pipeline(
        state,
        pregame,
        postgame,
    )


def apply_pregame_adjustments(
    home_elo: float,
    away_elo: float,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executes only pregame transformations.
    """

    state = {
        "home_elo": float(home_elo),
        "away_elo": float(away_elo),
        "context": dict(context),
        "config": config,
        "postgame": {},
    }

    pregame, _ = build_pipeline(config)

    return run_pregame_pipeline(
        state,
        pregame,
    )

def apply_postgame_adjustments(
    home_elo: float,
    away_elo: float,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executes only postgame transformations.
    """

    state = {
        "home_elo": float(home_elo),
        "away_elo": float(away_elo),
        "context": dict(context),
        "config": config,
        "postgame": {},
    }

    _, postgame = build_pipeline(config)

    return run_postgame_pipeline(
        state,
        postgame,
    )