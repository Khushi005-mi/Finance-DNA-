import pytest

from core.input_validation_layer import validate_input
from core.models import FinancialReport

def test_valid_input_returns_financial_report():
    payload = {
        "company_id": "TEST123",
        "fiscal_year": 2024,
        "data": {
            "total_revenue": 1_000_000,
            "fixed_cost_total": 200_000,
            "variable_cost_total": 300_000,
        }
    }

    result = validate_input(payload)

    assert isinstance(result, FinancialReport)
    assert result.company_id == "TEST123"
    assert result.fiscal_year == 2024

# Missing Required Field Must Fail
def test_missing_company_id_should_fail():
    payload = {
        "fiscal_year": 2024,
        "data": {}
    }

    with pytest.raises(Exception):
        validate_input(payload)

#   Wrong Data Type Should Fail
def test_fiscal_year_wrong_type():
    payload = {
        "company_id": "TEST",
        "fiscal_year": "2024",  # string instead of int
        "data": {}
    }

    with pytest.raises(Exception):
        validate_input(payload)

# Strict typing prevents downstream ambiguity.

# No implicit casting. No guessing.      

# Wrong Data Type Should Fail
def test_fiscal_year_wrong_type():
    payload = {
        "company_id": "TEST",
        "fiscal_year": "2024",  # string instead of int
        "data": {}
    }

    with pytest.raises(Exception):
        validate_input(payload)

# Strict typing prevents downstream ambiguity.

# No implicit casting. No guessing.
# Negative Fiscal Year Must Fail
def test_negative_fiscal_year():
    payload = {
        "company_id": "TEST",
        "fiscal_year": -2024,
        "data": {}
    }

    with pytest.raises(Exception):
        validate_input(payload)

# This is logical validation — not just structural.

# Empty Company ID Must Fail
def test_empty_company_id():
    payload = {
        "company_id": "",
        "fiscal_year": 2024,
        "data": {}
    }

    with pytest.raises(Exception):
        validate_input(payload)

# 6️⃣ Data Must Be Dictionary
def test_data_must_be_dict():
    payload = {
        "company_id": "TEST",
        "fiscal_year": 2024,
        "data": "not_a_dict"
    }

    with pytest.raises(Exception):
        validate_input(payload)

# 🔟 Reject Unknown Top-Level Fields (Strict Mode)

# Production systems must not silently accept extra fields.

def test_reject_unknown_fields():
    payload = {
        "company_id": "TEST",
        "fiscal_year": 2024,
        "data": {},
        "unexpected_field": "should_not_exist"
    }

    with pytest.raises(Exception):
        validate_input(payload)

# 9️⃣ Determinism
def test_validation_is_deterministic():
    payload = {
        "company_id": "TEST",
        "fiscal_year": 2024,
        "data": {}
    }

    r1 = validate_input(payload)
    r2 = validate_input(payload)

    assert r1 == r2

# 8️⃣ Extremely Large Numbers Should Be Accepted

# We test boundary without overflow.

def test_extremely_large_values():
    payload = {
        "company_id": "TEST",
        "fiscal_year": 2024,
        "data": {
            "total_revenue": 10**12,
            "fixed_cost_total": 10**11,
            "variable_cost_total": 10**11,
        }
    }

    result = validate_input(payload)

    assert result.data["total_revenue"] == 10**12

#7️⃣ Numeric Fields Must Be Numeric
def test_numeric_field_must_be_number():
    payload = {
        "company_id": "TEST",
        "fiscal_year": 2024,
        "data": {
            "total_revenue": "1M"
        }
    }

    with pytest.raises(Exception):
        validate_input(payload)

























