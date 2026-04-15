from typing import Dict, Any, List, Callable, Optional

Result = Dict[str, Any]
Rule = Callable[[Dict[str, Any], Dict[str, Any]], Optional[Result]]


# -------------------------
# Shared error builder
# -------------------------
def _build_error(code: str, message: str, field: str, severity: str) -> Result:
    return {
        "code": code,
        "message": message,
        "field": field,
        "severity": severity,
        "detected_at_layer": "PLAUSIBILITY",  # REQUIRED for audit + confidence attribution
    }


# -------------------------
# Blocking Rules
# -------------------------

def rule_zero_cost_positive_revenue(payload: Dict[str, Any], rules: Dict[str, Any]) -> Optional[Result]:
    revenue = payload.get("total_revenue")
    fixed_cost = payload.get("fixed_cost_total", 0)
    variable_cost = payload.get("variable_cost_total", 0)

    if revenue is not None and revenue > 0 and (fixed_cost + variable_cost) == 0:
        return _build_error(
            "ZERO_COST_WITH_POSITIVE_REVENUE",
            "Revenue exists with zero total cost",
            "total_cost",
            "BLOCKING",
        )

    return None


def rule_extreme_impossible_margin(payload: Dict[str, Any], rules: Dict[str, Any]) -> Optional[Result]:
    revenue = payload.get("total_revenue")
    fixed_cost = payload.get("fixed_cost_total", 0)
    variable_cost = payload.get("variable_cost_total", 0)

    # Guard 1 — invalid or non-positive revenue
    if revenue is None or revenue <= 0:
        return None

    # Guard 2 — minimum revenue floor to avoid tiny-number distortion
    min_revenue = rules.get("min_revenue_for_margin_check", 10_000)
    if revenue < min_revenue:
        return None

    total_cost = fixed_cost + variable_cost

    # Extreme margin threshold from rules
    threshold = rules.get("extreme_margin_ratio", 0.99)

    margin = 1 - (total_cost / revenue)

    if margin > threshold:
        return _build_error(
            "ECONOMIC_IMPOSSIBILITY_MARGIN",
            "Profit margin exceeds extreme plausible threshold",
            "total_revenue",
            "BLOCKING",
        )

    return None


# -------------------------
# Warning Rules
# -------------------------

def rule_currency_scale_anomaly(payload: Dict[str, Any], rules: Dict[str, Any]) -> Optional[Result]:
    revenue = payload.get("total_revenue")
    currency = payload.get("currency_code")

    currency_ranges = rules.get("currency_ranges", {})

    # Silence is intentional in Phase-3 (validation layer owns missing/unknown currency)
    if revenue is None or currency not in currency_ranges:
        return None

    lower, upper = currency_ranges[currency]

    if not (lower <= revenue <= upper):
        return _build_error(
            "CURRENCY_SCALE_ANOMALY",
            "Revenue magnitude inconsistent with currency scale",
            "total_revenue",
            "WARNING",
        )

    return None


def rule_negative_gross_margin(payload: Dict[str, Any], rules: Dict[str, Any]) -> Optional[Result]:
    revenue = payload.get("total_revenue")
    variable_cost = payload.get("variable_cost_total", 0)

    if revenue is not None and revenue > 0 and variable_cost > revenue:
        return _build_error(
            "NEGATIVE_GROSS_MARGIN",
            "Variable cost exceeds revenue",
            "variable_cost_total",
            "WARNING",
        )

    return None


# -------------------------
# Rule Registry
# -------------------------

PLAUSIBILITY_RULES: List[Rule] = [
    rule_zero_cost_positive_revenue,
    rule_extreme_impossible_margin,
    rule_currency_scale_anomaly,
    rule_negative_gross_margin,
]


# -------------------------
# Engine
# -------------------------

def plausibility_check(payload: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[Result] = []
    warnings: List[Result] = []

    for rule in PLAUSIBILITY_RULES:
        result = rule(payload, rules)

        if result is None:
            continue

        if result["severity"] == "BLOCKING":
            errors.append(result)
        else:
            warnings.append(result)

    is_blocked = len(errors) > 0
    is_valid = not is_blocked

    return {
        "is_valid": is_valid,
        "is_blocked": is_blocked,
        "errors": errors,
        "warnings": warnings,
    }


# from typing import Dict, Any, List, Callable, Optional

# Result = Dict[str, Any]
# Rule = Callable[[Dict[str, Any], Dict[str, Any]], Optional[Result]]


# def plausibility_check(payload: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
#     errors: List[Result] = []
#     warnings: List[Result] = []

#     for rule in PLAUSIBILITY_RULES:
#         result = rule(payload, rules)

#         if result is None:
#             continue

#         if result["severity"] == "BLOCKING":
#             errors.append(result)
#         else:
#             warnings.append(result)

#     is_blocked = len(errors) > 0
#     is_valid = not is_blocked

#     return {
#         "is_valid": is_valid,
#         "is_blocked": is_blocked,
#         "errors": errors,
#         "warnings": warnings,
#     }
# def rule_zero_cost_positive_revenue(payload, rules):
#     revenue = payload.get("total_revenue")
#     fixed_cost = payload.get("fixed_cost_total", 0)
#     variable_cost = payload.get("variable_cost_total", 0)

#     if revenue and revenue > 0 and (fixed_cost + variable_cost) == 0:
#         return {
#             "code": "ZERO_COST_WITH_POSITIVE_REVENUE",
#             "message": "Revenue exists with zero total cost",
#             "field": "total_cost",
#             "severity": "BLOCKING",
#         }
# def rule_currency_scale(payload, rules):
#     revenue = payload.get("total_revenue")
#     currency = payload.get("currency_code")

#     if revenue is None or currency not in rules:
#         return None

#     lower, upper = rules[currency]["revenue_range"]

#     if not (lower <= revenue <= upper):
#         return {
#             "code": "CURRENCY_SCALE_ANOMALY",
#             "message": "Revenue magnitude inconsistent with currency scale",
#             "field": "total_revenue",
#             "severity": "WARNING",
#         }
# def rule_negative_margin(payload, rules):
#     revenue = payload.get("total_revenue")
#     variable_cost = payload.get("variable_cost_total", 0)

#     if revenue and variable_cost > revenue:
#         return {
#             "code": "NEGATIVE_GROSS_MARGIN",
#             "message": "Variable cost exceeds revenue",
#             "field": "variable_cost_total",
#             "severity": "WARNING",
#         }
# PLAUSIBILITY_RULES: List[Rule] = [
#     rule_zero_cost_positive_revenue,
#     rule_currency_scale,
#     rule_negative_margin,
# ]



from core.config_loader import load_industry_rules


def check_industry_margin(metrics: dict, industry: str):
    rules = load_industry_rules()

    industry_config = rules.get(industry)
    if not industry_config:
        return []

    errors = []

    min_margin = industry_config.get("gross_margin_min")
    if metrics["gross_margin"] < min_margin:
        errors.append({
            "code": "LOW_GROSS_MARGIN",
            "severity": "WARNING"
        })

    return errors