"""
Core Elo calculations.

Implements the sport-independent Elo probability and rating
update functions used throughout the project.
"""

INITIAL_ELO = 1500
SEED = 42

# =========================
# Win PROBABILITY
# =========================

def win_probability(home_elo, away_elo):
    """
    Computes the home team's pregame win probability.

    Parameters
    ----------
    home_elo : float
        Home team's adjusted pregame Elo.

    away_elo : float
        Away team's adjusted pregame Elo.

    Returns
    -------
    float
        Probability that the home team wins.
    """
    return 1 / (1 + 10 ** ((away_elo - home_elo) / 400))


# =========================
# Elo UPDATE
# =========================

def update_elo(home_elo,
               away_elo,
               actual,
               p_home,
               k,
               multiplier=1.0):
    """
    Updates Elo ratings using an observed result and
    a precomputed win probability.

    Parameters
    ----------
    home_elo : float
        Home team's pregame Elo.

    away_elo : float
        Away team's pregame Elo.

    actual : int
        1 if home team won, 0 otherwise.

    p_home : float
        Pregame home win probability.

    k : float
        Elo K-factor.

    multiplier : float
        Elo update multiplier.

    Returns
    -------
    home_elo_new, away_elo_new
    """

    error = actual - p_home

    home_elo_new = home_elo + k * error * multiplier
    away_elo_new = away_elo - k * error * multiplier

    return home_elo_new, away_elo_new