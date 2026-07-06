"""
Sport configurations.

Defines sport-specific runtime defaults such as data paths,
initial Elo values, and default model selection.
"""

from ..engine.constants import INITIAL_ELO


# ==========================================================
# SPORT CONFIGURATIONS
# ==========================================================

SPORT_CONFIGS = {

    "NFL": {

        "schedule_path": "data/nfl_games.csv",

        "initial_elo": INITIAL_ELO,

        "default_model": "MOV_HFA",

    },

    "NHL": {

        "schedule_path": "data/nhl_games.csv",

        "initial_elo": INITIAL_ELO,

        "default_model": "MOV_HFA",

    },

}