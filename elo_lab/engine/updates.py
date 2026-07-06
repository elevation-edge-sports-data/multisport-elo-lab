"""
Elo rating updates.

Implements sport-independent Elo rating update functions.
"""

# =========================================================
# CORE UPDATE FUNCTION
# =========================================================

def update_ratings(
    home_elo: float,
    away_elo: float,
    actual: int,
    p_home: float,
    k: float,
    multiplier: float = 1.0,
):
    """
    Updates both team Elo ratings using the observed game result
    and the pregame home win probability.
    """

    error = actual - p_home

    home_new = home_elo + k * error * multiplier
    away_new = away_elo - k * error * multiplier

    return home_new, away_new


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def update_elo(*args, **kwargs):
    """
    Legacy alias for backward compatibility with older workflows.
    Redirects to update_ratings.
    """
    return update_ratings(*args, **kwargs)