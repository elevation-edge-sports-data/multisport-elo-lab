import numpy as np

def calibration_bins(probs, actuals, bins=10):
    probs = np.array(probs)
    actuals = np.array(actuals)

    bin_edges = np.linspace(0, 1, bins + 1)
    results = []

    for i in range(bins):
        mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])

        if np.sum(mask) == 0:
            continue

        avg_prob = np.mean(probs[mask])
        avg_actual = np.mean(actuals[mask])

        results.append({
            "bin": i,
            "pred_prob": avg_prob,
            "actual_rate": avg_actual,
            "count": np.sum(mask)
        })

    return results


def probability_stats(probs):
    probs = np.array(probs)
    return {
        "mean": np.mean(probs),
        "std": np.std(probs),
        "min": np.min(probs),
        "max": np.max(probs)
    }