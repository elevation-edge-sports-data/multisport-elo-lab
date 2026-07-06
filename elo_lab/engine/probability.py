"""
Elo probability calculations.

Implements sport-independent Elo probability functions.
"""

# ==========================================================
# WIN PROBABILITY
# ==========================================================

def win_probability(home_elo: float, away_elo: float) -> float:
    """
    Computes the home team's pregame win probability using the
    standard Elo logistic formulation.
    """

    return 1.0 / (1.0 + 10 ** ((away_elo - home_elo) / 400.0))