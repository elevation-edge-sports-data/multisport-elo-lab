INITIAL_ELO = 1500
SEED = 42


# =========================
# Win probability function
# =========================

def win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


# =========================
# Elo update function
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