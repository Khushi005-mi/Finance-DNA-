import time
import logging
from typing import Dict, Any
logger = logging.getLogger(__name__)
# Track startup time
START_TIME = time.time()

# Example dependency flags (expand later)
_dependencies: Dict[str, bool] = {
    "core_engine": True,
    # "database": False,
    # "redis": False,
}
def set_dependency_status(name: str, status: bool) -> None:
    """
    Update dependency health dynamically.
    """
    _dependencies[name] = status
def get_uptime_seconds() -> int:
    return int(time.time() - START_TIME)

def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe:
    Only verifies the application process is running.
    Must NEVER check external dependencies.
    """
    return {
        "status": "alive",
        "uptime_seconds": get_uptime_seconds(),
    }
def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe:
    Verifies system can handle requests.
    Should validate critical dependencies.
    """
    unhealthy = [k for k, v in _dependencies.items() if not v]

    if unhealthy:
        logger.error(
            "Readiness check failed",
            extra={"failed_dependencies": unhealthy},
        )
        return {
            "status": "not_ready",
            "failed_dependencies": unhealthy,
        }

    return {
        "status": "ready",
        "uptime_seconds": get_uptime_seconds(),
        "dependencies": _dependencies,
    }