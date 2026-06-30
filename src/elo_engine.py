INITIAL_ELO = 1500
K = 20
HFA = 55
SEED = 42


# =========================
# Win probability function
# =========================

def win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


# =========================
# Basic Elo update function
# =========================

def update_elo(home_elo, away_elo, home_score, away_score):

    # Compute result
    home_win = 1 if home_score > away_score else 0

    # Compute probability
    p_home = win_prob(home_elo, away_elo)

    # Compute error
    error = home_win - p_home

    # Update
    home_elo_new = home_elo + K * error
    away_elo_new = away_elo - K * error

    # Return
    return home_elo_new, away_elo_new, p_home