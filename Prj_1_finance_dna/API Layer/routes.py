from fastapi import APIRouter, HTTPException, Request, status
from api.request_models import FinancialReportRequest
from api.response_models import FinanceDNAResponse
from core.models import FinancialReport
from core.orchestration import run_pipeline
import logging
import uuid
import time

router = APIRouter()
logger = logging.getLogger("finance_dna_api")
logger.setLevel(logging.INFO)

@router.post("/compute_finance_dna", response_model=FinanceDNAResponse)
async def compute_finance_dna(request: Request, payload: FinancialReportRequest):
    """
    Production-ready API endpoint for Finance DNA:
    Metrics, Risk, Confidence, Warnings
    """
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"Request received", extra={"trace_id": trace_id})

    try:
        # Convert request to FinancialReport
        report = FinancialReport(
            company_id=payload.company_id,
            fiscal_year=payload.fiscal_year,
            data=payload.data
        )

        # Run pipeline
        result = run_pipeline(report)

        # Log successful completion
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "Pipeline completed successfully",
            extra={"trace_id": trace_id, "latency_ms": latency_ms}
        )

        # Add trace_id to response
        result["trace_id"] = trace_id
        return result

    except ValueError as ve:
        # Known validation / business errors
        logger.warning(f"Validation error: {ve}", extra={"trace_id": trace_id})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    except Exception as e:
        # Unknown internal errors
        logger.error(f"Internal server error: {e}", extra={"trace_id": trace_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")