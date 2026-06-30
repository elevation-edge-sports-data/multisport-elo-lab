# Accuracy

def accuracy(preds, actuals):
    return sum(p == a for p, a in zip(preds, actuals)) / len(preds)

# Log Loss

import numpy as np

def log_loss(p, y):
    eps = 1e-15
    p = min(max(p, eps), 1 - eps)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))

# Brier Score

def brier(p, y):
    return (p - y) ** 2