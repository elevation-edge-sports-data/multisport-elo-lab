"""
NFL team metadata.

Canonical metadata used throughout the Version 6 dashboard.

Fields
------
name            : Full team name
conference      : AFC / NFC
division        : East / North / South / West
primary_color   : Official primary team color (hex)
secondary_color : Official secondary/accent color (hex)
logo            : Logo filename in app/assets/logos/
"""

NFL_TEAMS = {

    # =========================
    # AFC EAST
    # =========================

    "BUF": {
        "name": "Buffalo Bills",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#00338D",
        "secondary_color": "#C60C30",
        "logo": "BUF.png",
    },

    "MIA": {
        "name": "Miami Dolphins",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#008E97",
        "secondary_color": "#FC4C02",
        "logo": "MIA.png",
    },

    "NE": {
        "name": "New England Patriots",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#002244",
        "secondary_color": "#C60C30",
        "logo": "NE.png",
    },

    "NYJ": {
        "name": "New York Jets",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#125740",
        "secondary_color": "#FFFFFF",
        "logo": "NYJ.png",
    },

    # =========================
    # AFC NORTH
    # =========================

    "BAL": {
        "name": "Baltimore Ravens",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#241773",
        "secondary_color": "#000000",
        "logo": "BAL.png",
    },

    "CIN": {
        "name": "Cincinnati Bengals",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#FB4F14",
        "secondary_color": "#000000",
        "logo": "CIN.png",
    },

    "CLE": {
        "name": "Cleveland Browns",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#311D00",
        "secondary_color": "#FF3C00",
        "logo": "CLE.png",
    },

    "PIT": {
        "name": "Pittsburgh Steelers",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#FFB612",
        "secondary_color": "#101820",
        "logo": "PIT.png",
    },

    # =========================
    # AFC SOUTH
    # =========================

    "HOU": {
        "name": "Houston Texans",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#03202F",
        "secondary_color": "#A71930",
        "logo": "HOU.png",
    },

    "IND": {
        "name": "Indianapolis Colts",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#002C5F",
        "secondary_color": "#A2AAAD",
        "logo": "IND.png",
    },

    "JAX": {
        "name": "Jacksonville Jaguars",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#006778",
        "secondary_color": "#101820",
        "logo": "JAX.png",
    },

    "TEN": {
        "name": "Tennessee Titans",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#0C2340",
        "secondary_color": "#4B92DB",
        "logo": "TEN.png",
    },

    # =========================
    # AFC WEST
    # =========================

    "DEN": {
        "name": "Denver Broncos",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#FB4F14",
        "secondary_color": "#002244",
        "logo": "DEN.png",
    },

    "KC": {
        "name": "Kansas City Chiefs",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#E31837",
        "secondary_color": "#FFB81C",
        "logo": "KC.png",
    },

    "LV": {
        "name": "Las Vegas Raiders",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#000000",
        "secondary_color": "#A5ACAF",
        "logo": "LV.png",
    },

    "LAC": {
        "name": "Los Angeles Chargers",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#0080C6",
        "secondary_color": "#FFC20E",
        "logo": "LAC.png",
    },

    # =========================
    # NFC EAST
    # =========================

    "DAL": {
        "name": "Dallas Cowboys",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#003594",
        "secondary_color": "#869397",
        "logo": "DAL.png",
    },

    "NYG": {
        "name": "New York Giants",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#0B2265",
        "secondary_color": "#A71930",
        "logo": "NYG.png",
    },

    "PHI": {
        "name": "Philadelphia Eagles",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#004C54",
        "secondary_color": "#A5ACAF",
        "logo": "PHI.png",
    },

    "WAS": {
        "name": "Washington Commanders",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#5A1414",
        "secondary_color": "#FFB612",
        "logo": "WAS.png",
    },

    # =========================
    # NFC NORTH
    # =========================

    "CHI": {
        "name": "Chicago Bears",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#0B162A",
        "secondary_color": "#C83803",
        "logo": "CHI.png",
    },

    "DET": {
        "name": "Detroit Lions",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#0076B6",
        "secondary_color": "#B0B7BC",
        "logo": "DET.png",
    },

    "GB": {
        "name": "Green Bay Packers",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#203731",
        "secondary_color": "#FFB612",
        "logo": "GB.png",
    },

    "MIN": {
        "name": "Minnesota Vikings",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#4F2683",
        "secondary_color": "#FFC62F",
        "logo": "MIN.png",
    },

    # =========================
    # NFC SOUTH
    # =========================

    "ATL": {
        "name": "Atlanta Falcons",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#A71930",
        "secondary_color": "#000000",
        "logo": "ATL.png",
    },

    "CAR": {
        "name": "Carolina Panthers",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#0085CA",
        "secondary_color": "#101820",
        "logo": "CAR.png",
    },

    "NO": {
        "name": "New Orleans Saints",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#D3BC8D",
        "secondary_color": "#101820",
        "logo": "NO.png",
    },

    "TB": {
        "name": "Tampa Bay Buccaneers",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#D50A0A",
        "secondary_color": "#34302B",
        "logo": "TB.png",
    },

    # =========================
    # NFC WEST
    # =========================

    "ARI": {
        "name": "Arizona Cardinals",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#97233F",
        "secondary_color": "#000000",
        "logo": "ARI.png",
    },

    "LAR": {
        "name": "Los Angeles Rams",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#003594",
        "secondary_color": "#FFD100",
        "logo": "LAR.png",
    },

    "SF": {
        "name": "San Francisco 49ers",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#AA0000",
        "secondary_color": "#B3995D",
        "logo": "SF.png",
    },

    "SEA": {
        "name": "Seattle Seahawks",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#002244",
        "secondary_color": "#69BE28",
        "logo": "SEA.png",
    },
}