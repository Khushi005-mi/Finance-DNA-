from pydantic import BaseModel, Field, ConfigDict
from typing import Dict , List, Optional

# Metrics Section
class MetricsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gross_margin: Optional [float] = Field(None, description="Gross margin ratio")
    net_margin :Optional [float] = Field(None, description="None income divided by revenue")
    return_on_equity: Optional[float] = Field(None, description="ROE ratio")
    debt_to_equity: Optional[float] = Field(None, description="Debt to equity ratio")
    current_ratio: Optional[float] = Field(None, description="Liquidity ratio")
    interest_coverage_ratio: Optional[float] = Field(None, description="EBIT / interest expense")


# -----------------------------
# Risk Section
# -----------------------------

class RiskModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(..., ge=0.0, le=1.0, description="Normalized risk score (0=low, 1=high)")
    risk_level: str = Field(..., description="Categorical risk level (LOW, MEDIUM, HIGH)")
    risk_flags: List[str] = Field(default_factory=list, description="Triggered risk flags")
# -----------------------------
# Confidence Section
# -----------------------------

class ConfidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall reliability score of the output"
    )

    metric_confidence: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence score per metric"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings affecting confidence"
    )
    # Top-Level API Response

class FinanceDNAResponse(BaseModel):
    """
    Fully structured Finance DNA API response.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str = Field(..., description="Company identifier")
    trace_id: str = Field(..., description="Trace ID for request observability")
    fiscal_year: int = Field(..., description="Fiscal year analyzed")

    metrics: MetricsModel
    risk: RiskModel
    confidence: ConfidenceModel

    