from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import uuid


# =========================================================
# Shared error builder
# =========================================================
def _build_error(code: str, message: str, field: str, severity: str) -> Dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "field": field,
        "severity": severity,
    }


# =========================================================
# Safe numeric extractor
# =========================================================
def _num(value) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    return None


# =========================================================
# Severity + Rule version
# =========================================================
SEVERITY_ERROR = "ERROR"
SEVERITY_WARNING = "WARNING"
RULE_VERSION = "2026.02.v1"


# =========================================================
# Base rules
# =========================================================
BASE_RULES = {
    "min_revenue_for_margin_check": 10_000,
    "extreme_margin_ratio": 0.99,
    "currency_ranges": {
        "USD": (1_000, 10_000_000_000, 100_000_000_000),
        "INR": (10_000, 1_000_000_000_000, 10_000_000_000_000),
        "JPY": (10_000, 1_000_000_000_000, 10_000_000_000_000),
    },
}


# =========================================================
# Industry overrides
# =========================================================
INDUSTRY_CONFIG = {
    "saas": {
        "extreme_margin_ratio": 0.99,
        "expected_variable_cost_ratio_max": 0.40,
    },
    "manufacturing": {
        "extreme_margin_ratio": 0.50,
        "expected_variable_cost_ratio_max": 0.80,
    },
    "retail": {
        "extreme_margin_ratio": 0.90,
        "expected_variable_cost_ratio_max": 0.90,
    },
}


# =========================================================
# Structural validation
# =========================================================
def validation_check(payload: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    revenue = _num(payload.get("total_revenue"))
    currency = payload.get("currency_code")

    if revenue is None:
        errors.append(_build_error("MISSING_REVENUE", "Revenue is required", "total_revenue", SEVERITY_ERROR))
    elif currency in rules["currency_ranges"]:
        low, soft_high, hard_high = rules["currency_ranges"][currency]

        if revenue < low or revenue > hard_high:
            errors.append(
                _build_error("CURRENCY_OUT_OF_HARD_RANGE", "Revenue outside hard currency bounds", "total_revenue", SEVERITY_ERROR)
            )
        elif revenue > soft_high:
            warnings.append(
                _build_error("CURRENCY_SCALE_ANOMALY", "Revenue outside expected currency scale", "total_revenue", SEVERITY_WARNING)
            )

    return {
        "is_blocked": any(e["severity"] == SEVERITY_ERROR for e in errors),
        "errors": errors,
        "warnings": warnings,
    }


# =========================================================
# Plausibility rules
# =========================================================
Rule = Callable[[Dict[str, Any], Dict[str, Any]], Optional[Dict[str, Any]]]


def rule_zero_cost_positive_revenue(payload, rules):
    revenue = _num(payload.get("total_revenue"))
    fixed_cost = _num(payload.get("fixed_cost_total")) or 0
    variable_cost = _num(payload.get("variable_cost_total")) or 0

    if revenue and revenue > 0 and fixed_cost == 0 and variable_cost == 0:
        return _build_error("ZERO_COST_WITH_POSITIVE_REVENUE", "Revenue exists but costs are zero", "fixed_cost_total", SEVERITY_ERROR)


def rule_negative_margin(payload, rules):
    revenue = _num(payload.get("total_revenue"))
    fixed_cost = _num(payload.get("fixed_cost_total")) or 0
    variable_cost = _num(payload.get("variable_cost_total")) or 0

    if revenue and (fixed_cost + variable_cost) > revenue:
        return _build_error("NEGATIVE_GROSS_MARGIN", "Costs exceed revenue", "variable_cost_total", SEVERITY_WARNING)


def rule_extreme_margin(payload, rules):
    revenue = _num(payload.get("total_revenue"))
    fixed_cost = _num(payload.get("fixed_cost_total")) or 0
    variable_cost = _num(payload.get("variable_cost_total")) or 0

    if not revenue or revenue <= 0:
        return None

    margin_ratio = 1 - ((fixed_cost + variable_cost) / revenue)

    if margin_ratio > rules.get("extreme_margin_ratio", 1):
        return _build_error("ECONOMIC_IMPOSSIBILITY_MARGINS", "Margin exceeds realistic bound", "total_revenue", SEVERITY_ERROR)


def rule_variable_cost_ratio(payload, rules):
    revenue = _num(payload.get("total_revenue"))
    variable_cost = _num(payload.get("variable_cost_total")) or 0

    if not revenue or revenue <= 0:
        return None

    max_ratio = rules.get("expected_variable_cost_ratio_max")
    if max_ratio is None:
        return None

    if (variable_cost / revenue) > max_ratio:
        return _build_error(
            "VARIABLE_COST_RATIO_ABOVE_INDUSTRY_NORM",
            "Variable cost ratio exceeds industry expectation",
            "variable_cost_total",
            SEVERITY_WARNING,
        )


PLAUSIBILITY_RULES: List[Rule] = [
    rule_zero_cost_positive_revenue,
    rule_negative_margin,
    rule_extreme_margin,
    rule_variable_cost_ratio,
]


# =========================================================
# Plausibility engine
# =========================================================
def plausibility_check(payload: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    for rule in PLAUSIBILITY_RULES:
        result = rule(payload, rules)
        if result:
            if result["severity"] == SEVERITY_ERROR:
                errors.append(result)
            else:
                warnings.append(result)

    return {
        "is_blocked": any(e["severity"] == SEVERITY_ERROR for e in errors),
        "errors": errors,
        "warnings": warnings,
    }


# =========================================================
# Strict industry resolver
# =========================================================
def get_industry_rules(industry: str) -> Dict[str, Any]:
    if industry not in INDUSTRY_CONFIG:
        raise ValueError(f"Unsupported industry_type: {industry}")
    return INDUSTRY_CONFIG[industry]


# =========================================================
# Full pipeline
# =========================================================
def run_financial_validation_pipeline(payload: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:

    # 1. Structural validation
    validation_result = validation_check(payload, rules)
    if validation_result["is_blocked"]:
        return {
            "audit": {
                "timestamp": datetime.utcnow().isoformat(),
                "validation_id": str(uuid.uuid4()),
                "rule_version": RULE_VERSION,
            },
            "is_valid": False,
            "is_blocked": True,
            "validation": validation_result,
            "plausibility": {"errors": [], "warnings": []},
        }

    # 2. Merge industry rules (strict)
    industry = payload.get("industry_type")
    industry_rules = get_industry_rules(industry)
    merged_rules = {**rules, **industry_rules}

    # 3. Plausibility checks
    plausibility_result = plausibility_check(payload, merged_rules)

    # 4. Final decision
    return {
        "audit": {
            "timestamp": datetime.utcnow().isoformat(),
            "validation_id": str(uuid.uuid4()),
            "rule_version": RULE_VERSION,
        },
        "is_valid": not plausibility_result["is_blocked"],
        "is_blocked": plausibility_result["is_blocked"],
        "validation": validation_result,
        "plausibility": plausibility_result,
    }


# =========================================================
# Sample run
# =========================================================
if __name__ == "__main__":
    sample_payload = {
        "total_revenue": 500_000,
        "fixed_cost_total": 0,
        "variable_cost_total": 0,
        "currency_code": "USD",
        "industry_type": "saas",
    }

    print(run_financial_validation_pipeline(sample_payload, BASE_RULES))
