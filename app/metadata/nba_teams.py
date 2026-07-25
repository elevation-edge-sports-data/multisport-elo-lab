"""
NBA team metadata.

Fields match nhl_teams.py / nfl_teams.py:
  name, conference, division, primary_color, secondary_color, logo
"""

from typing import Dict, Optional

NBA_TEAMS: Dict[str, Dict] = {
    # Eastern - Atlantic
    "BOS": {
        "name": "Boston Celtics",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#007A33",
        "secondary_color": "#BA9653",
        "logo": "BOS.png",
    },
    "BKN": {
        "name": "Brooklyn Nets",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#000000",
        "secondary_color": "#FFFFFF",
        "logo": "BKN.png",
    },
    "NYK": {
        "name": "New York Knicks",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#006BB6",
        "secondary_color": "#F58426",
        "logo": "NYK.png",
    },
    "PHI": {
        "name": "Philadelphia 76ers",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#006BB6",
        "secondary_color": "#ED174C",
        "logo": "PHI.png",
    },
    "TOR": {
        "name": "Toronto Raptors",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#CE1141",
        "secondary_color": "#000000",
        "logo": "TOR.png",
    },
    # Eastern - Central
    "CHI": {
        "name": "Chicago Bulls",
        "conference": "Eastern",
        "division": "Central",
        "primary_color": "#CE1141",
        "secondary_color": "#000000",
        "logo": "CHI.png",
    },
    "CLE": {
        "name": "Cleveland Cavaliers",
        "conference": "Eastern",
        "division": "Central",
        "primary_color": "#860038",
        "secondary_color": "#FDBB30",
        "logo": "CLE.png",
    },
    "DET": {
        "name": "Detroit Pistons",
        "conference": "Eastern",
        "division": "Central",
        "primary_color": "#C8102E",
        "secondary_color": "#1D42BA",
        "logo": "DET.png",
    },
    "IND": {
        "name": "Indiana Pacers",
        "conference": "Eastern",
        "division": "Central",
        "primary_color": "#002D62",
        "secondary_color": "#FDBB30",
        "logo": "IND.png",
    },
    "MIL": {
        "name": "Milwaukee Bucks",
        "conference": "Eastern",
        "division": "Central",
        "primary_color": "#00471B",
        "secondary_color": "#EEE1C6",
        "logo": "MIL.png",
    },
    # Eastern - Southeast
    "ATL": {
        "name": "Atlanta Hawks",
        "conference": "Eastern",
        "division": "Southeast",
        "primary_color": "#E03A3E",
        "secondary_color": "#C1D32F",
        "logo": "ATL.png",
    },
    "CHA": {
        "name": "Charlotte Hornets",
        "conference": "Eastern",
        "division": "Southeast",
        "primary_color": "#1D1160",
        "secondary_color": "#00788C",
        "logo": "CHA.png",
    },
    "MIA": {
        "name": "Miami Heat",
        "conference": "Eastern",
        "division": "Southeast",
        "primary_color": "#98002E",
        "secondary_color": "#F9A01B",
        "logo": "MIA.png",
    },
    "ORL": {
        "name": "Orlando Magic",
        "conference": "Eastern",
        "division": "Southeast",
        "primary_color": "#0077C0",
        "secondary_color": "#C4CED4",
        "logo": "ORL.png",
    },
    "WAS": {
        "name": "Washington Wizards",
        "conference": "Eastern",
        "division": "Southeast",
        "primary_color": "#002B5C",
        "secondary_color": "#E31837",
        "logo": "WAS.png",
    },
    # Western - Northwest
    "DEN": {
        "name": "Denver Nuggets",
        "conference": "Western",
        "division": "Northwest",
        "primary_color": "#0E2240",
        "secondary_color": "#FEC524",
        "logo": "DEN.png",
    },
    "MIN": {
        "name": "Minnesota Timberwolves",
        "conference": "Western",
        "division": "Northwest",
        "primary_color": "#0C2340",
        "secondary_color": "#236192",
        "logo": "MIN.png",
    },
    "OKC": {
        "name": "Oklahoma City Thunder",
        "conference": "Western",
        "division": "Northwest",
        "primary_color": "#007AC1",
        "secondary_color": "#EF3B24",
        "logo": "OKC.png",
    },
    "POR": {
        "name": "Portland Trail Blazers",
        "conference": "Western",
        "division": "Northwest",
        "primary_color": "#E03A3E",
        "secondary_color": "#000000",
        "logo": "POR.png",
    },
    "UTA": {
        "name": "Utah Jazz",
        "conference": "Western",
        "division": "Northwest",
        "primary_color": "#002B5C",
        "secondary_color": "#00471B",
        "logo": "UTA.png",
    },
    # Western - Pacific
    "GSW": {
        "name": "Golden State Warriors",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#1D428A",
        "secondary_color": "#FFC72C",
        "logo": "GSW.png",
    },
    "LAC": {
        "name": "Los Angeles Clippers",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#C8102E",
        "secondary_color": "#1D428A",
        "logo": "LAC.png",
    },
    "LAL": {
        "name": "Los Angeles Lakers",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#552583",
        "secondary_color": "#FDB927",
        "logo": "LAL.png",
    },
    "PHX": {
        "name": "Phoenix Suns",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#1D1160",
        "secondary_color": "#E56020",
        "logo": "PHX.png",
    },
    "SAC": {
        "name": "Sacramento Kings",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#5A2D81",
        "secondary_color": "#63727A",
        "logo": "SAC.png",
    },
    # Western - Southwest
    "DAL": {
        "name": "Dallas Mavericks",
        "conference": "Western",
        "division": "Southwest",
        "primary_color": "#00538C",
        "secondary_color": "#002B5E",
        "logo": "DAL.png",
    },
    "HOU": {
        "name": "Houston Rockets",
        "conference": "Western",
        "division": "Southwest",
        "primary_color": "#CE1141",
        "secondary_color": "#000000",
        "logo": "HOU.png",
    },
    "MEM": {
        "name": "Memphis Grizzlies",
        "conference": "Western",
        "division": "Southwest",
        "primary_color": "#5D76A9",
        "secondary_color": "#12173F",
        "logo": "MEM.png",
    },
    "NOP": {
        "name": "New Orleans Pelicans",
        "conference": "Western",
        "division": "Southwest",
        "primary_color": "#0C2340",
        "secondary_color": "#C8102E",
        "logo": "NOP.png",
    },
    "SAS": {
        "name": "San Antonio Spurs",
        "conference": "Western",
        "division": "Southwest",
        "primary_color": "#C4CED4",
        "secondary_color": "#000000",
        "logo": "SAS.png",
    },
}


def get_nba_teams(conference: Optional[str] = None) -> Dict[str, Dict]:
    """Return all teams, or only those in the given conference."""
    if conference is None:
        return NBA_TEAMS
    return {
        abbr: info
        for abbr, info in NBA_TEAMS.items()
        if info["conference"] == conference
    }


def get_nba_team_colors(team_abbr: str) -> tuple[str, str]:
    """Return (primary_color, secondary_color). Defaults to black/white."""
    info = NBA_TEAMS.get(team_abbr.upper())
    if info is None:
        return "#000000", "#FFFFFF"
    return info["primary_color"], info["secondary_color"]