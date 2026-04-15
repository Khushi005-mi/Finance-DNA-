from core.metrics_engine import compute_metrics
from core.risk_scoring import compute_risk
from core.confidence_engine import compute_confidence
from input_validation_layer import validate_report
from core.models import FinancialReport
import logging
import uuid

# Optional: structured logging setup
logger = logging.getLogger("finance_dna_pipeline")
logger.setLevel(logging.INFO)

def run_pipeline(report: FinancialReport) -> dict:
    """
    Run the full Finance DNA pipeline:
      1. Validate input
      2. Compute metrics
      3. Compute risk score
      4. Compute confidence
      5. Return structured output
    
    Returns:
        dict: {
            "report_id": str,
            "metrics": dict,
            "risk": dict,
            "confidence": dict
        }
    """
    # Generate trace ID for observability
    trace_id = str(uuid.uuid4())
    logger.info(f"Pipeline started", extra={"trace_id": trace_id, "company_id": report.company_id})

    # 1️⃣ Input Validation
    validate_report(report)
    logger.info("Input validated", extra={"trace_id": trace_id})

    # 2️⃣ Metrics Calculation
    metrics = compute_metrics(report)
    logger.info("Metrics computed", extra={"trace_id": trace_id, "metrics": metrics})

    # 3️⃣ Risk Scoring
    risk_result = compute_risk(metrics)
    logger.info("Risk scored", extra={"trace_id": trace_id, "risk_result": risk_result})

    # 4️⃣ Confidence Calculation
    confidence_result = compute_confidence(metrics, risk_result)
    logger.info("Confidence computed", extra={"trace_id": trace_id, "confidence_result": confidence_result})

    # 5️⃣ Return full structured output
    output = {
        "report_id": report.company_id,
        "trace_id": trace_id,
        "metrics": metrics,
        "risk": risk_result,
        "confidence": confidence_result
    }
    logger.info("Pipeline completed", extra={"trace_id": trace_id})

    return output
