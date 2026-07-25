"""
NHL venue / elevation metadata.

Stadium elevations in feet. No elevation bins are currently used
by the model for NHL (Elevation Edge is NFL-only for now).
"""

from typing import Dict

NHL_VENUES: Dict[str, Dict] = {
    "ANA": {"elevation_ft": 164,  "notes": ""},
    "BOS": {"elevation_ft": 10,   "notes": ""},
    "BUF": {"elevation_ft": 600,  "notes": ""},
    "CAR": {"elevation_ft": 400,  "notes": ""},
    "CBJ": {"elevation_ft": 725,  "notes": ""},
    "CGY": {"elevation_ft": 3430, "notes": ""},
    "CHI": {"elevation_ft": 600,  "notes": ""},
    "COL": {"elevation_ft": 5280, "notes": "Highest NHL arena"},
    "DAL": {"elevation_ft": 482,  "notes": ""},
    "DET": {"elevation_ft": 597,  "notes": ""},
    "EDM": {"elevation_ft": 2200, "notes": ""},
    "FLA": {"elevation_ft": 10,   "notes": ""},
    "LAK": {"elevation_ft": 250,  "notes": ""},
    "MIN": {"elevation_ft": 823,  "notes": ""},
    "MTL": {"elevation_ft": 174,  "notes": ""},
    "NJD": {"elevation_ft": 13,   "notes": ""},
    "NSH": {"elevation_ft": 554,  "notes": ""},
    "NYI": {"elevation_ft": 552,  "notes": ""},
    "NYR": {"elevation_ft": 36,   "notes": ""},
    "OTT": {"elevation_ft": 328,  "notes": ""},
    "PHI": {"elevation_ft": 40,   "notes": ""},
    "PIT": {"elevation_ft": 853,  "notes": ""},
    "SEA": {"elevation_ft": 100,  "notes": ""},
    "SJS": {"elevation_ft": 82,   "notes": ""},
    "STL": {"elevation_ft": 466,  "notes": ""},
    "TBL": {"elevation_ft": 36,   "notes": ""},
    "TOR": {"elevation_ft": 249,  "notes": ""},
    "UTA": {"elevation_ft": 4327, "notes": ""},
    "VAN": {"elevation_ft": 30,   "notes": ""},
    "VGK": {"elevation_ft": 2020, "notes": ""},
    "WPG": {"elevation_ft": 774,  "notes": ""},
    "WSH": {"elevation_ft": 40,   "notes": ""},
}


def get_elevation_bins() -> Dict[str, int]:
    """NHL does not currently use elevation bins. Returns empty mapping."""
    return {}


def get_elevation_ft() -> Dict[str, int]:
    """Return {abbr: elevation_ft}."""
    return {abbr: info["elevation_ft"] for abbr, info in NHL_VENUES.items()}
