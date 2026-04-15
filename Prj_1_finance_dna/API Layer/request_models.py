from pydantic import BaseModel,Field, field_validator,ConfigDict #Pydantic adds runtime overhead.
# It performs validation at object creation.
# It can mask performance issues in tight loops.
# It is ideal at API boundaries, not inside numeric engines.
from typing import Dict
from datetime import datetime

class FinancialReportRequest(BaseModel):
    """
    API level input model for FinanceDNA pipeline.
    Stictly validates incoming financial data before
    passing it to the core layer."""

    model_config = ConfigDict(
        extra = "forbid",
        str_strip_whitespace=True
    )
    company_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique company identifier"
    )

    data: Dict[str, float] = Field(
        ...,description="Dictionary of financial fields(revenue, net_income, etc.)"
    )
    # Validators
    @field_validator("company_id")
    @classmethod
    def validate_required_fields(cls,value: Dict[str, float]):
        required_fields = {
            "revenue",
            "gross_profit",
            "net_income",
            "total_assets",
            "shareholder_equity"

        }
        missing = required_fields - value.keys()
        if missing:
            raise ValueError(f"Missing required financial fields: {missing}")
        
        return value
        