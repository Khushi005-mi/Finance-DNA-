# core/confidence_engine.py
from typing import Dict, Any

def compute_confidence(metrics: Dict[str, float], risk_result: Dict[str, any]) -> Dict[str, Any]:
    """
    Compute a confidence score for the pipeline output.
    
    Args:
        metrics: dict of computed financial metrics
        risk_result: output from compute_risk(), contains:
                     {"risk_score": float, "risk_flags": list[str]}
                     
    Returns:
        {
            "overall_confidence": float (0-1),
            "per_metric_confidence": Dict[str, float],
            "warnings": List[str]
        }
    """
    per_metric_confidence = {}
    warnings = []

    # Base confidence
    base_confidence = 1.0

    # 1️⃣ Penalize missing metrics
    for metric, value in metrics.items():
        if value is None:
            per_metric_confidence[metric] = 0.0
            warnings.append(f"Missing metric: {metric}")
            base_confidence -= 0.1
        else:
            per_metric_confidence[metric] = 1.0

    # 2️⃣ Penalize risk flags
    for flag in risk_result.get("risk_flags", []):
        base_confidence -= 0.1
        warnings.append(f"Risk flag: {flag}")

    # 3️⃣ Clamp overall confidence between 0 and 1
    overall_confidence = max(min(base_confidence, 1.0), 0.0)

    return {
        "overall_confidence": overall_confidence,
        "per_metric_confidence": per_metric_confidence,
        "warnings": warnings
    }


from core.config_loader import load_pipeline_config


def calculate_confidence_score(errors: list) -> float:
    config = load_pipeline_config()

    warning_penalty = config["confidence"]["warning_penalty"]
    block_penalty = config["confidence"]["block_penalty"]

    score = 1.0

    for e in errors:
        if e["severity"] == "WARNING":
            score -= warning_penalty
        elif e["severity"] == "BLOCK":
            score -= block_penalty

    return max(0.0, score)