import numpy as np

# =========================
# Margin of Victory Multiplier
# =========================

def mov_multiplier(home_score, away_score):
    """
    Returns the Elo multiplier based on margin of victory.
    """
    margin = abs(home_score - away_score)
    return np.log(margin + 1)