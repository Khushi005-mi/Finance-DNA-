# core/risk_scoring.py
from typing import Dict, Tuple

# Config-driven thresholds and weights
METRIC_CONFIG = {
    "net_margin": {"weight": 0.3, "threshold": 0, "type": "min"},
    "ROE": {"weight": 0.2, "threshold": 0, "type": "min"},
    "debt_to_equity": {"weight": 0.2, "threshold": 2, "type": "max"},
    "current_ratio": {"weight": 0.15, "threshold": 1, "type": "min"},
    "interest_coverage": {"weight": 0.15, "threshold": 1, "type": "min"}
}

def compute_risk(metrics: Dict[str, float]) -> Dict[str, any]:
    """
    Compute risk score from metrics dict.
    Returns:
        {
            "risk_score": float (0-1),
            "risk_flags": list[str]
        }
    """
    total_weight = sum(config["weight"] for config in METRIC_CONFIG.values())
    risk_score = 0.0
    risk_flags = []

    for metric, config in METRIC_CONFIG.items():
        value = metrics.get(metric, None)
        if value is None:
            # Missing metrics contribute max risk
            metric_risk = 1.0
            risk_flags.append(f"Missing {metric}")
        else:
            # Check threshold
            if config["type"] == "min":
                if value < config["threshold"]:
                    metric_risk = 1.0
                    risk_flags.append(f"{metric} below threshold")
                else:
                    metric_risk = 0.0
            elif config["type"] == "max":
                if value > config["threshold"]:
                    metric_risk = 1.0
                    risk_flags.append(f"{metric} above threshold")
                else:
                    metric_risk = 0.0
            else:
                metric_risk = 0.0

        # Weighted contribution
        risk_score += metric_risk * config["weight"]

    # Normalize by total weight
    risk_score /= total_weight
    risk_score = min(max(risk_score, 0.0), 1.0)  # Clamp 0-1

    return {"risk_score": risk_score, "risk_flags": risk_flags}
from core.config_loader import load_industry_rules, load_pipeline_config


def calculate_risk_score(metrics: dict, industry: str = None) -> float:
    config = load_pipeline_config()
    rules = load_industry_rules()

    weights = config["risk_scoring"]["weights"]

    score = (
        weights["gross_margin"] * (1 - metrics["gross_margin"]) +
        weights["operating_margin"] * (1 - metrics["operating_margin"]) +
        weights["debt_ratio"] * metrics["debt_ratio"]
    )

    if config["features"]["enable_industry_adjustment"] and industry:
        industry_config = rules.get(industry)
        if industry_config:
            multiplier = industry_config.get("risk_multiplier", 1.0)
            score *= multiplier

    return max(0.0, min(1.0, score))




