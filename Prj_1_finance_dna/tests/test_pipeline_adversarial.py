import pytest
from  full_pipeline_intigration import run_financial_validation_pipeline


def valid_payload():
    return {
        "total_revenue": 500000,
        "fixed_cost_total": 100000,
        "variable_cost_total": 200000,
        "currency_code": "USD",
        "industry_type": "saas",
    }


def test_boolean_revenue_blocked():
    payload = valid_payload()
    payload["total_revenue"] = True

    result = run_financial_validation_pipeline(payload)

    assert result["is_blocked"] is True
    assert any(e["code"] == "INVALID_NUMERIC_TYPE" for e in result["errors"])


def test_string_revenue_blocked():
    payload = valid_payload()
    payload["total_revenue"] = "500000"

    result = run_financial_validation_pipeline (payload)

    assert result["is_blocked"] is True
    assert any(e["code"] == "INVALID_NUMERIC_TYPE" for e in result["errors"])


def test_missing_required_field_blocked():
    payload = valid_payload()
    del payload["total_revenue"]

    result = run_financial_validation_pipeline(payload)
    assert result["is_blocked"] is True
    assert any(e["code"] == "MISSING_REQUIRED_FIELD" for e in result["errors"])


def test_negative_revenue_blocked():
    payload = valid_payload()
    payload["total_revenue"] = -1

    result = run_financial_validation_pipeline(payload)

    assert result["is_blocked"] is True


def test_extreme_large_number_handled():
    payload = valid_payload()
    payload["total_revenue"] = 10**18

    result = run_financial_validation_pipeline(payload)

    assert result is not None


def test_variable_cost_exceeds_revenue():
    payload = valid_payload()
    payload["variable_cost_total"] = 600000

    result = run_financial_validation_pipeline(payload)

    assert any(
        e["severity"] in ["WARNING", "BLOCK"]
        for e in result["errors"]
    )