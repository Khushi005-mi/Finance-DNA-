from prometheus_client import Counter, Histogram, Gauge

# Total API requests
REQUEST_COUNT = Counter(
    "finance_dna_requests_total",
    "Total number of Finance DNA API requests"
)

# Total pipeline failures
PIPELINE_FAILURES = Counter(
    "finance_dna_pipeline_failures_total",
    "Total number of pipeline failures"
)

# Validation failures
VALIDATION_FAILURES = Counter(
    "finance_dna_validation_failures_total",
    "Total number of validation failures"
)

# Full pipeline execution time (seconds)
PIPELINE_DURATION = Histogram(
    "finance_dna_pipeline_duration_seconds",
    "Time spent executing full Finance DNA pipeline",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5)
)

# Current in-flight requests
IN_PROGRESS_REQUESTS = Gauge(
    "finance_dna_in_progress_requests",
    "Number of requests currently being processed"
)

# Optional: track risk score distribution
RISK_SCORE_DISTRIBUTION = Histogram(
    "finance_dna_risk_score_distribution",
    "Distribution of computed risk scores",
    buckets=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
)