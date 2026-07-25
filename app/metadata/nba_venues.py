"""
NBA venue / elevation metadata.

Stadium elevations in feet. Prepared for future NBA support.
"""

from typing import Dict

NBA_VENUES: Dict[str, Dict] = {
    "ATL": {"elevation_ft": 1050, "notes": ""},
    "BKN": {"elevation_ft": 49,   "notes": ""},
    "BOS": {"elevation_ft": 10,   "notes": ""},
    "CHA": {"elevation_ft": 721,  "notes": ""},
    "CHI": {"elevation_ft": 600,  "notes": ""},
    "CLE": {"elevation_ft": 582,  "notes": ""},
    "DAL": {"elevation_ft": 482,  "notes": ""},
    "DEN": {"elevation_ft": 5280, "notes": "Highest NBA arena"},
    "DET": {"elevation_ft": 597,  "notes": ""},
    "GSW": {"elevation_ft": 13,   "notes": ""},
    "HOU": {"elevation_ft": 45,   "notes": ""},
    "IND": {"elevation_ft": 707,  "notes": ""},
    "LAC": {"elevation_ft": 135,  "notes": ""},
    "LAL": {"elevation_ft": 250,  "notes": ""},
    "MEM": {"elevation_ft": 338,  "notes": ""},
    "MIA": {"elevation_ft": 7,    "notes": ""},
    "MIL": {"elevation_ft": 593,  "notes": ""},
    "MIN": {"elevation_ft": 845,  "notes": ""},
    "NOP": {"elevation_ft": 2,    "notes": ""},
    "NYK": {"elevation_ft": 36,   "notes": ""},
    "OKC": {"elevation_ft": 1200, "notes": ""},
    "ORL": {"elevation_ft": 106,  "notes": ""},
    "PHI": {"elevation_ft": 40,   "notes": ""},
    "PHX": {"elevation_ft": 1117, "notes": ""},
    "POR": {"elevation_ft": 92,   "notes": ""},
    "SAC": {"elevation_ft": 34,   "notes": ""},
    "SAS": {"elevation_ft": 662,  "notes": ""},
    "TOR": {"elevation_ft": 249,  "notes": ""},
    "UTA": {"elevation_ft": 4327, "notes": ""},
    "WAS": {"elevation_ft": 40,   "notes": ""},
}


def get_elevation_bins() -> Dict[str, int]:
    """NBA does not currently use elevation bins. Returns empty mapping."""
    return {}


def get_elevation_ft() -> Dict[str, int]:
    """Return {abbr: elevation_ft}."""
    return {abbr: info["elevation_ft"] for abbr, info in NBA_VENUES.items()}
