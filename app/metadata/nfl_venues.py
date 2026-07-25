"""
NFL venue / elevation metadata.

Single source of truth for stadium elevation (feet) and the
Elevation Edge bins used by the model.
"""

from typing import Dict

NFL_VENUES: Dict[str, Dict] = {
    "ARI": {"elevation_ft": 1070, "elevation_bin": 4, "notes": ""},
    "ATL": {"elevation_ft": 1050, "elevation_bin": 3, "notes": ""},
    "BAL": {"elevation_ft": 10,   "elevation_bin": 0, "notes": ""},
    "BUF": {"elevation_ft": 770,  "elevation_bin": 3, "notes": ""},
    "CAR": {"elevation_ft": 746,  "elevation_bin": 2, "notes": ""},
    "CHI": {"elevation_ft": 600,  "elevation_bin": 1, "notes": ""},
    "CIN": {"elevation_ft": 486,  "elevation_bin": 2, "notes": ""},
    "CLE": {"elevation_ft": 580,  "elevation_bin": 2, "notes": ""},
    "DAL": {"elevation_ft": 604,  "elevation_bin": 0, "notes": ""},
    "DEN": {"elevation_ft": 5280, "elevation_bin": 5, "notes": "Mile High"},
    "DET": {"elevation_ft": 552,  "elevation_bin": 1, "notes": ""},
    "GB":  {"elevation_ft": 640,  "elevation_bin": 2, "notes": ""},
    "HOU": {"elevation_ft": 49,   "elevation_bin": 1, "notes": ""},
    "IND": {"elevation_ft": 705,  "elevation_bin": 2, "notes": ""},
    "JAX": {"elevation_ft": 4,    "elevation_bin": 1, "notes": ""},
    "KC":  {"elevation_ft": 840,  "elevation_bin": 3, "notes": ""},
    "LAC": {"elevation_ft": 125,  "elevation_bin": 0, "notes": ""},
    "LAR": {"elevation_ft": 125,  "elevation_bin": 0, "notes": ""},
    "LV":  {"elevation_ft": 2190, "elevation_bin": 4, "notes": ""},
    "MIA": {"elevation_ft": 10,   "elevation_bin": 0, "notes": ""},
    "MIN": {"elevation_ft": 840,  "elevation_bin": 1, "notes": ""},
    "NE":  {"elevation_ft": 298,  "elevation_bin": 0, "notes": ""},
    "NO":  {"elevation_ft": 3,    "elevation_bin": 0, "notes": ""},
    "NYG": {"elevation_ft": 7,    "elevation_bin": 0, "notes": ""},
    "NYJ": {"elevation_ft": 7,    "elevation_bin": 0, "notes": ""},
    "PHI": {"elevation_ft": 39,   "elevation_bin": 1, "notes": ""},
    "PIT": {"elevation_ft": 725,  "elevation_bin": 2, "notes": ""},
    "SEA": {"elevation_ft": 46,   "elevation_bin": 0, "notes": ""},
    "SF":  {"elevation_ft": 16,   "elevation_bin": 0, "notes": ""},
    "TB":  {"elevation_ft": 36,   "elevation_bin": 0, "notes": ""},
    "TEN": {"elevation_ft": 450,  "elevation_bin": 1, "notes": ""},
    "WAS": {"elevation_ft": 160,  "elevation_bin": 1, "notes": ""},
}


def get_elevation_bins() -> Dict[str, int]:
    """Return {abbr: elevation_bin} for use by Elevation Edge."""
    return {abbr: info["elevation_bin"] for abbr, info in NFL_VENUES.items()}


def get_elevation_ft() -> Dict[str, int]:
    """Return {abbr: elevation_ft}."""
    return {abbr: info["elevation_ft"] for abbr, info in NFL_VENUES.items()}
