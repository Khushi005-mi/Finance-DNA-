from datetime import datetime
from typing import Dict, Any, List


# -------------------------
# Error builder (single source of truth)
# -------------------------
def _build_error(
    code: str,
    message: str,
    field: str,
    severity: str = "BLOCKING",
) -> Dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "field": field,
        "severity": severity,
        "detected_at_layer": "INPUT_VALIDATION",
    }


# -------------------------
# Atomic numeric validation
# -------------------------
def _validate_numeric(
    value: Any,
    field: str,
    constraints: Dict[str, Any],
    errors: List[Dict[str, Any]],
) -> bool:
    # Type validation (structured + atomic)
    if not isinstance(value, (int, float)):
        errors.append(
            _build_error(
                code="INVALID_TYPE",
                message=f"{field} must be numeric",
                field=field,
            )
        )
        return False

    # Domain constraints
    if "min" in constraints and value < constraints["min"]:
        errors.append(
            _build_error(
                code="VALUE_BELOW_MIN",
                message=f"{field} is below minimum allowed value",
                field=field,
            )
        )
        return False

    if "max" in constraints and value > constraints["max"]:
        errors.append(
            _build_error(
                code="VALUE_ABOVE_MAX",
                message=f"{field} exceeds maximum allowed value",
                field=field,
            )
        )
        return False

    return True


# -------------------------
# Period validation (consistent model)
# -------------------------
def _validate_period(
    period: Any,
    allowed_periods: List[str],
    errors: List[Dict[str, Any]],
) -> bool:
    if not isinstance(period, str):
        errors.append(
            _build_error(
                code="INVALID_PERIOD_TYPE",
                message="Period must be a string",
                field="period",
            )
        )
        return False

    if period not in allowed_periods:
        errors.append(
            _build_error(
                code="INVALID_PERIOD",
                message="Period is not aligned with allowed reporting periods",
                field="period",
            )
        )
        return False

    return True


# -------------------------
# Main validation function
# -------------------------
def validation_financial_input(
    payload: Dict[str, Any],
    schema_rules: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Pure input validation.
    No normalization. No classification. No confidence scoring.
    """

    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    validated_fields: List[str] = []
    missing_fields: List[str] = []

    required_fields = schema_rules.get("required_fields", [])
    numeric_constraints = schema_rules.get("numeric_constraints", {})
    allowed_enums = schema_rules.get("allowed_enums", {})
    period_rules = schema_rules.get("period_rules", {})

    # -------------------------
    # Required field validation (atomic)
    # -------------------------
    for field in required_fields:
        if field not in payload or payload[field] is None:
            missing_fields.append(field)
            errors.append(
                _build_error(
                    code="MISSING_FIELD",
                    message="Required field is missing",
                    field=field,
                )
            )

    # -------------------------
    # ENUM validation (atomic)
    # -------------------------
    for field, allowed_values in allowed_enums.items():
        if field in payload:
            if payload[field] not in allowed_values:
                errors.append(
                    _build_error(
                        code="INVALID_ENUM",
                        message=f"Invalid value for {field}",
                        field=field,
                    )
                )
            else:
                validated_fields.append(field)

    # -------------------------
    # Numeric validation (atomic + truthful)
    # -------------------------
    for field, constraints in numeric_constraints.items():
        if field in payload:
            ok = _validate_numeric(
                value=payload[field],
                field=field,
                constraints=constraints,
                errors=errors,
            )
            if ok:
                validated_fields.append(field)

    # -------------------------
    # Period validation (consistent model)
    # -------------------------
    period = payload.get("period")
    allowed_periods = period_rules.get("allowed_periods", [])

    if period is not None:
        if _validate_period(period, allowed_periods, errors):
            validated_fields.append("period")

    # -------------------------
    # Cross-field economic blocking rules
    # -------------------------
    revenue = payload.get("revenue")
    profit = payload.get("profit")
    employees = payload.get("employees")

    # Economic impossibilities → BLOCK
    if revenue is not None and revenue < 0:
        errors.append(
            _build_error(
                code="NEGATIVE_REVENUE",
                message="Revenue cannot be negative",
                field="revenue",
            )
        )

    if profit is not None and revenue is not None and profit > revenue:
        errors.append(
            _build_error(
                code="IMPOSSIBLE_PROFIT",
                message="Profit cannot exceed revenue",
                field="profit",
            )
        )

    if revenue is not None and revenue > 0 and employees == 0:
        errors.append(
            _build_error(
                code="ECONOMIC_IMPOSSIBILITY",
                message="Revenue cannot exist with zero employees",
                field="employees",
            )
        )

    # -------------------------
    # Warning rules (non-blocking signals)
    # -------------------------
    growth = payload.get("growth_rate")
    if isinstance(growth, (int, float)) and growth > 500:
        warnings.append(
            _build_error(
                code="SUSPICIOUS_GROWTH",
                message="Growth rate is unusually high",
                field="growth_rate",
                severity="WARNING",
            )
        )

    # -------------------------
    # Final decision flags
    # -------------------------
    is_blocked = any(err["severity"] == "BLOCKING" for err in errors)
    is_valid = not is_blocked

    # -------------------------
    # Result object
    # -------------------------
    return {
        "is_valid": is_valid,
        "is_blocked": is_blocked,
        "errors": errors,
        "warnings": warnings,
        "validated_fields": list(set(validated_fields)),
        "missing_fields": missing_fields,
        "timestamp": datetime.utcnow().isoformat(),
        "rule_version": schema_rules.get("rule_version", "v1"),
    }
## financial_intelligence/
# │
# ├── validation.py          # Phase 2 — input & structural validation
# ├── plausibility.py        # Phase 3 — economic sanity & plausibility
# ├── normalization.py       # Phase 4 — currency, period, scaling
# ├── classification.py      # Phase 6 — cost structure labeling
# ├── confidence.py          # Phase 7 — confidence decay & scoring
# ├── orchestration.py       # Phase 8 — pipeline coordination
# │
# ├── models/
# │   └── result_objects.py
# │
# ├── tests/
# │   ├── test_validation.py
# │   ├── test_plausibility.py
# │   └── test_cases_matrix.py
