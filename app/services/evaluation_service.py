from elo_lab.workflows.evaluate_models import evaluate_models


def get_model_metrics():
    """
    Returns the current model evaluation summary.
    """
    return evaluate_models()