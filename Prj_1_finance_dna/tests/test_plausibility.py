import pytest

from core.plausibility import evaluate_plausibility
from core.models import FinancialReport
@pytest.fixture
def valid_report():
    return FinancialReport(
        company_id="TEST",
        fiscal_year=2024,
        data={
            "total_revenue": 1_000_000,
            "fixed_cost_total": 200_000,
            "variable_cost_total": 300_000,
        }
    )
# Clean Case Must Produce No BLOCK Errors
def test_valid_report_no_blocks(valid_report):
    errors = evaluate_plausibility(valid_report)

    assert not any(e["severity"] == "BLOCK" for e in errors)

# If valid data triggers blocks → your rules are unstable.

# Variable Cost > Revenue

# Economically impossible in normal conditions.

def test_variable_cost_exceeds_revenue():
    report = FinancialReport(
        company_id="TEST",
        fiscal_year=2024,
        data={
            "total_revenue": 500_000,
            "fixed_cost_total": 100_000,
            "variable_cost_total": 600_000,
        }
    )

    errors = evaluate_plausibility(report)

    assert any(
        e["code"] == "VARIABLE_COST_EXCEEDS_REVENUE"
        for e in errors
    )

# This enforces cross-field sanity.


# Unrealistic Margin Warning
# Example rule: gross margin > 95% may be suspicious.
def test_extreme_margin_warning():
    report = FinancialReport(
        company_id="TEST",
        fiscal_year=2024,
        data={
            "total_revenue": 1_000_000,
            "fixed_cost_total": 10,
            "variable_cost_total": 10,
        }
    )

    errors = evaluate_plausibility(report)

    assert any(
        e["severity"] == "WARNING"
        for e in errors
    )
# You are testing detection of outliers.
# Determinism
def test_plausibility_deterministic(valid_report):
    e1 = evaluate_plausibility(valid_report)
    e2 = evaluate_plausibility(valid_report)

    assert e1 == e2
# If this fails, your rules contain hidden state.
# That’s dangerous.

# Severity Classification Stability
def test_block_severity_is_consistent():
    report = FinancialReport(
        company_id="TEST",
        fiscal_year=2024,
        data={
            "total_revenue": 100,
            "fixed_cost_total": 10,
            "variable_cost_total": 200,
        }
    )

    errors = evaluate_plausibility(report)

    block_errors = [e for e in errors if e["severity"] == "BLOCK"]

    assert len(block_errors) > 0
# This ensures rule strength remains intact.




# Empty Data Handling
def test_missing_fields_handled_gracefully():
    report = FinancialReport(
        company_id="TEST",
        fiscal_year=2024,
        data={}
    )

    errors = evaluate_plausibility(report)

    assert isinstance(errors, list)

# Plausibility must not crash on incomplete data.