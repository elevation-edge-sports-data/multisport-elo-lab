"""
NHL team metadata including colors, conferences, divisions for multisport dashboard.
Mirrors structure of nfl_teams.py for minimal drift.
"""

NHL_TEAMS = {
    # Eastern Conference - Atlantic Division
    "BOS": {
        "name": "Boston Bruins",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#FCB514",
        "secondary_color": "#111111",
        "logo": "BOS.png"
    },
    "BUF": {
        "name": "Buffalo Sabres",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#002654",
        "secondary_color": "#FCB514",
        "logo": "BUF.png"
    },
    "DET": {
        "name": "Detroit Red Wings",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#C8102E",
        "secondary_color": "#FFFFFF",
        "logo": "DET.png"
    },
    "FLA": {
        "name": "Florida Panthers",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#C8102E",
        "secondary_color": "#041E42",
        "logo": "FLA.png"
    },
    "MTL": {
        "name": "Montreal Canadiens",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#C8102E",
        "secondary_color": "#FFFFFF",
        "logo": "MTL.png"
    },
    "OTT": {
        "name": "Ottawa Senators",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#C8102E",
        "secondary_color": "#C5C5C5",
        "logo": "OTT.png"
    },
    "TBL": {
        "name": "Tampa Bay Lightning",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#00205B",
        "secondary_color": "#FFFFFF",
        "logo": "TBL.png"
    },
    "TOR": {
        "name": "Toronto Maple Leafs",
        "conference": "Eastern",
        "division": "Atlantic",
        "primary_color": "#00205B",
        "secondary_color": "#FFFFFF",
        "logo": "TOR.png"
    },
    # Eastern - Metropolitan
    "CAR": {
        "name": "Carolina Hurricanes",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#CC0000",
        "secondary_color": "#000000",
        "logo": "CAR.png"
    },
    "CBJ": {
        "name": "Columbus Blue Jackets",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#002654",
        "secondary_color": "#CE1126",
        "logo": "CBJ.png"
    },
    "NJD": {
        "name": "New Jersey Devils",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#C8102E",
        "secondary_color": "#000000",
        "logo": "NJD.png"
    },
    "NYI": {
        "name": "New York Islanders",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#00539B",
        "secondary_color": "#F47D30",
        "logo": "NYI.png"
    },
    "NYR": {
        "name": "New York Rangers",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#0038A8",
        "secondary_color": "#C8102E",
        "logo": "NYR.png"
    },
    "PHI": {
        "name": "Philadelphia Flyers",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#F36C21",
        "secondary_color": "#000000",
        "logo": "PHI.png"
    },
    "PIT": {
        "name": "Pittsburgh Penguins",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#000000",
        "secondary_color": "#FFB81C",
        "logo": "PIT.png"
    },
    "WSH": {
        "name": "Washington Capitals",
        "conference": "Eastern",
        "division": "Metropolitan",
        "primary_color": "#C8102E",
        "secondary_color": "#041E42",
        "logo": "WSH.png"
    },
    # Western - Central
    "CHI": {
        "name": "Chicago Blackhawks",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#C8102E",
        "secondary_color": "#000000",
        "logo": "CHI.png"
    },
    "COL": {
        "name": "Colorado Avalanche",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#6F263D",
        "secondary_color": "#236192",
        "logo": "COL.png"
    },
    "DAL": {
        "name": "Dallas Stars",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#00843D",
        "secondary_color": "#A7A9AC",
        "logo": "DAL.png"
    },
    "MIN": {
        "name": "Minnesota Wild",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#154734",
        "secondary_color": "#A6192E",
        "logo": "MIN.png"
    },
    "NSH": {
        "name": "Nashville Predators",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#FFB81C",
        "secondary_color": "#041E42",
        "logo": "NSH.png"
    },
    "STL": {
        "name": "St. Louis Blues",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#002F87",
        "secondary_color": "#FCB514",
        "logo": "STL.png"
    },
    "UTA": {
        "name": "Utah Hockey Club",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#3A8BCE",
        "secondary_color": "#000000",
        "logo": "UTA.png"
    },
    "WPG": {
        "name": "Winnipeg Jets",
        "conference": "Western",
        "division": "Central",
        "primary_color": "#041E42",
        "secondary_color": "#AC2F3A",
        "logo": "WPG.png"
    },
    # Western - Pacific
    "ANA": {
        "name": "Anaheim Ducks",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#F47A38",
        "secondary_color": "#B5985A",
        "logo": "ANA.png"
    },
    "CGY": {
        "name": "Calgary Flames",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#C8102E",
        "secondary_color": "#F1BE48",
        "logo": "CGY.png"
    },
    "EDM": {
        "name": "Edmonton Oilers",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#00205B",
        "secondary_color": "#FF4C00",
        "logo": "EDM.png"
    },
    "LAK": {
        "name": "Los Angeles Kings",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#111111",
        "secondary_color": "#A2AAAD",
        "logo": "LAK.png"
    },
    "SJS": {
        "name": "San Jose Sharks",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#006D75",
        "secondary_color": "#EA7200",
        "logo": "SJS.png"
    },
    "SEA": {
        "name": "Seattle Kraken",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#001F5B",
        "secondary_color": "#68A2B9",
        "logo": "SEA.png"
    },
    "VAN": {
        "name": "Vancouver Canucks",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#00205B",
        "secondary_color": "#FFD100",
        "logo": "VAN.png"
    },
    "VGK": {
        "name": "Vegas Golden Knights",
        "conference": "Western",
        "division": "Pacific",
        "primary_color": "#B4975A",
        "secondary_color": "#000000",
        "logo": "VGK.png"
    },
}

# Helper to get all teams for a conference or all
def get_nhl_teams(conference=None):
    if conference:
        return {k: v for k, v in NHL_TEAMS.items() if v["conference"] == conference}
    return NHL_TEAMS

def get_nhl_team_colors(team_abbr):
    team = NHL_TEAMS.get(team_abbr, {})
    return team.get("primary_color", "#000000"), team.get("secondary_color", "#FFFFFF")