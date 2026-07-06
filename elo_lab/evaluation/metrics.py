"""
Evaluation metrics for Elo model performance.

Implements standard classification and probabilistic scoring
metrics used across backtesting and parameter optimization.
"""

import numpy as np

def accuracy(probs, actuals):
    probs = np.array(probs)
    actuals = np.array(actuals)
    preds = (probs >= 0.5).astype(int)
    return np.mean(preds == actuals)


def log_loss(p, y):
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def brier(p, y):
    return (p - y) ** 2