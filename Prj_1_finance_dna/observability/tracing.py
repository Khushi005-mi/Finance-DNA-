import uuid
import time
import logging
from contextvars import ContextVar
from functools import wraps

# Context variable for request trace ID
# Context variable for request trace ID
_trace_id_ctx_var: ContextVar[str | None] = ContextVar("trace_id", default=None)

logger = logging.getLogger(__name__)

def generate_trace_id() -> str:
    """
    Generate a unique trace ID per request.
    """
    return uuid.uuid4().hex


def set_trace_id(trace_id: str) -> None:
    """
    Store trace_id in context for current request.
    """
    _trace_id_ctx_var.set(trace_id)


def get_trace_id() -> str | None:
    """
    Retrieve current trace_id.
    """
    return _trace_id_ctx_var.get()


def clear_trace_id() -> None:
    """
    Clear trace_id after request finishes.
    """
    _trace_id_ctx_var.set(None)

def traced_span(span_name: str):
    """
    Decorator to trace execution time of critical blocks.
    Adds structured logging automatically.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = get_trace_id()
            start_time = time.time()

            logger.info(
                f"{span_name} started",
                extra={"trace_id": trace_id},
            )
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    f"{span_name} completed",
                    extra={
                        "trace_id": trace_id,
                        "duration_ms": duration_ms,
                    },
                )
                return result
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                logger.error(
                    f"{span_name} failed",
                    extra={
                        "trace_id": trace_id,
                        "duration_ms": duration_ms,
                        "error": str(e),
                    },
                )
                raise

        return wrapper

    return decorator














