from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class SeverityLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class FinancialInput:
    """
    Immutable financial payload contract.
    Must pass validation before entering core logic.
    """
    revenue: float
    cogs: float
    operating_expenses: float
    currency: str
    period_months: int
    industry: str


@dataclass(frozen=True)
class ErrorDetail:
    """
    Structured error contract.
    """
    code: str
    message: str
    field: Optional[str]
    severity: SeverityLevel


@dataclass
class ValidationResult:
    """
    Output of validation layers.
    """
    is_blocked: bool
    errors: List[ErrorDetail] = field(default_factory=list)


@dataclass
class PipelineResult:
    """
    Final pipeline output.
    """
    input_data: FinancialInput
    validation: ValidationResult
    risk_score: Optional[float]
    derived_metrics: Optional[dict]