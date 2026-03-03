# core/metrics_engine.py
from typing import Dict
from core.models import FinancialReport

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Avoid division by zero and missing values."""
    try:
        if denominator in (0, None):
            return default
        return numerator / denominator
    except Exception:
        return default

def compute_metrics(report: FinancialReport) -> Dict[str, float]:
    """Compute financial metrics from a FinancialReport object."""
    
    data = report.data  # raw financial numbers
    metrics = {}

    # Profitability
    metrics['gross_margin'] = safe_divide(data.get('gross_profit', 0), data.get('revenue', 0))
    metrics['net_margin'] = safe_divide(data.get('net_income', 0), data.get('revenue', 0))
    metrics['ROA'] = safe_divide(data.get('net_income', 0), data.get('total_assets', 0))
    metrics['ROE'] = safe_divide(data.get('net_income', 0), data.get('shareholder_equity', 0))

    # Liquidity
    metrics['current_ratio'] = safe_divide(data.get('current_assets', 0), data.get('current_liabilities', 0))
    metrics['quick_ratio'] = safe_divide(
        data.get('current_assets', 0) - data.get('inventory', 0),
        data.get('current_liabilities', 0)
    )

    # Leverage
    metrics['debt_to_equity'] = safe_divide(data.get('total_debt', 0), data.get('shareholder_equity', 0))
    metrics['interest_coverage'] = safe_divide(data.get('EBIT', 0), data.get('interest_expense', 0))

    # Efficiency
    metrics['asset_turnover'] = safe_divide(data.get('revenue', 0), data.get('total_assets', 0))
    metrics['inventory_turnover'] = safe_divide(data.get('COGS', 0), data.get('inventory', 0))

    return metrics
