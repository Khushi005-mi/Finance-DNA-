import math
import pytest
from core.risk_scoring import compute_risk
from core.confidence_engine import compute_confidence


# ==========================
# RISK ENGINE TESTS
# ==========================

def test_risk_score_bounds():
    metrics = {
        "gross_margin": 0.6,
        "operating_margin": 0.4,
        "break_even_ratio": 0.3,
    }
    score = compute_risk(metrics)
    assert 0 <= score <= 100


def test_risk_score_deterministic():
    metrics = {
        "gross_margin": 0.6,
        "operating_margin": 0.4,
        "break_even_ratio": 0.3,
    }

    s1 = compute_risk(metrics)
    s2 = compute_risk(metrics)

    assert s1 == s2


def test_risk_increases_when_margins_drop():
    good_metrics = {
        "gross_margin": 0.7,
        "operating_margin": 0.5,
        "break_even_ratio": 0.2,
    }

    bad_metrics = {
        "gross_margin": 0.1,
        "operating_margin": 0.05,
        "break_even_ratio": 0.9,
    }

    good_score = compute_risk(good_metrics)
    bad_score = compute_risk(bad_metrics)

    assert bad_score > good_score


def test_extreme_metric_values():
    extreme_metrics = {
        "gross_margin": 0.0,
        "operating_margin": 0.0,
        "break_even_ratio": 1.0,
    }

    score = compute_risk(extreme_metrics)
    assert 0 <= score <= 100


def test_risk_score_precision():
    metrics = {
        "gross_margin": 0.3333333,
        "operating_margin": 0.2222222,
        "break_even_ratio": 0.1111111,
    }

    score = compute_risk(metrics)
    assert isinstance(score, float)


# ==========================
# CONFIDENCE ENGINE TESTS
# ==========================

def test_confidence_bounds():
    metrics = {
        "gross_margin": 0.6,
        "operating_margin": 0.4,
    }
    errors = []

    confidence = compute_confidence(metrics, errors)
    assert 0 <= confidence <= 1


def test_confidence_decrease_with_errors():
    metrics = {
        "gross_margin": 0.6,
        "operating_margin": 0.4,
    }

    no_error_conf = compute_confidence(metrics, [])

    some_errors = [
        {"severity": "WARNING"},
        {"severity": "BLOCK"},
    ]

    degraded_conf = compute_confidence(metrics, some_errors)
    assert degraded_conf < no_error_conf


def test_confidence_deterministic():
    metrics = {
        "gross_margin": 0.6,
        "operating_margin": 0.4,
    }

    errors = [{"severity": "WARNING"}]

    c1 = compute_confidence(metrics, errors)
    c2 = compute_confidence(metrics, errors)

    assert math.isclose(c1, c2, rel_tol=1e-9)


def test_confidence_missing_metrics():
    incomplete_metrics = {}
    confidence = compute_confidence(incomplete_metrics, [])
    assert confidence < 1


def test_high_risk_not_high_confidence():
    high_risk_metrics = {
        "gross_margin": 0.05,
        "operating_margin": 0.02,
        "break_even_ratio": 0.95,
    }

    risk = compute_risk(high_risk_metrics)
    confidence = compute_confidence(high_risk_metrics, [])

    assert not (risk > 80 and confidence > 0.9)