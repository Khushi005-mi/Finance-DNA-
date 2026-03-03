import pytest
import math

from core.risk_scoring import calculate_risk_score
from core.confidence_engine import calculate_confidence_score

# 1️⃣ Risk Score Must Stay Within Bounds
def test_risk_score_within_bounds():
    metrics = {
        "gross_margin": 0.4,
        "operating_margin": 0.2,
        "debt_ratio": 0.3,
    }

    score = calculate_risk_score(metrics)

    assert 0.0 <= score <= 1.0


# 2️⃣ Determinism
def test_risk_score_deterministic():
    metrics = {
        "gross_margin": 0.5,
        "operating_margin": 0.3,
        "debt_ratio": 0.2,
    }

    s1 = calculate_risk_score(metrics)
    s2 = calculate_risk_score(metrics)

    assert s1 == s2
# 3️⃣ Higher Debt → Higher Risk
def test_debt_increases_risk():
    low_debt = {
        "gross_margin": 0.4,
        "operating_margin": 0.2,
        "debt_ratio": 0.1,
    }

    high_debt = {
        "gross_margin": 0.4,
        "operating_margin": 0.2,
        "debt_ratio": 0.8,
    }

    r_low = calculate_risk_score(low_debt)
    r_high = calculate_risk_score(high_debt)

    assert r_high > r_low


    # 4️⃣ Higher Margin → Lower Risk
def test_margin_reduces_risk():
    weak_margin = {
        "gross_margin": 0.1,
        "operating_margin": 0.05,
        "debt_ratio": 0.3,
    }

    strong_margin = {
        "gross_margin": 0.6,
        "operating_margin": 0.4,
        "debt_ratio": 0.3,
    }

    r_weak = calculate_risk_score(weak_margin)
    r_strong = calculate_risk_score(strong_margin)

    assert r_strong < r_weak

# 5️⃣ Extreme Worst Case Should Approach 1.0
def test_extreme_worst_case():
    metrics = {
        "gross_margin": -0.2,
        "operating_margin": -0.1,
        "debt_ratio": 1.5,
    }

    score = calculate_risk_score(metrics)

    assert score > 0.8

# Your model must meaningfully respond to catastrophic metrics.





