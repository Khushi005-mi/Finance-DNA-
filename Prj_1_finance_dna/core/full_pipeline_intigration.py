from typing import Dict, Any


def run_financial_validation_pipeline(
    payload: Dict[str, Any],
    rules: Dict[str, Any]
) -> Dict[str, Any]:

    # ---------- 1. Structural validation ----------
    validation_result = validation_check(payload, rules)

    # If structural layer blocks → stop immediately
    if validation_result["is_blocked"]:
        return {
            "is_valid": False,
            "is_blocked": True,
            "validation": {
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
            },
            "plausibility": {
                "errors": [],
                "warnings": [],
            },
        }

    # ---------- 2. Economic plausibility ----------
    plausibility_result = plausibility_check(payload, rules)

    # ---------- 3. Final decision ----------
    is_blocked = plausibility_result["is_blocked"]
    is_valid = not is_blocked

    return {
        "is_valid": is_valid,
        "is_blocked": is_blocked,
        "validation": {
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"],
        },
        "plausibility": {
            "errors": plausibility_result["errors"],
            "warnings": plausibility_result["warnings"],
        },
    }
