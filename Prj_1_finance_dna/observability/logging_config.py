import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger

LOG_FORMAT = (
    "%(asctime)",
    "%(levelname)s",
    "%(name)s",
    "%(message)s",
    "%(trace_id)s",
    "%(company_id)s",
    "%(fiscal_year)s"
)

class ContextFilter (logging.Filter):
 """
 Ensures required structured fields always exist.
 Prevents KeyError in JSON formatter
 """   

def filter(self, record: logging.LogRecord) -> bool:
    if not hasattr(record, "trace_id"):
       record.trace_id = None
    if not hasattr(record, "company_id"):
       record.company_id = None
    if not hasattr(record, "fiscal_id"): 
       record.fiscal_year = None
    return True

def setup_logging(level: Optional[str] = "INFO") -> None:
   """
   Configure structured JSON logging for the entire application.
   Should be called at once at application startup.
   """ 
   root_logger = logging.getLogger()    
    # Prevent duplicate handlers in reload environments
   if root_logger.handlers:
        root_logger.handlers.clear()

        root_logger.setLevel(level)

        handler = logging.StreamHandler(sys.stdout)

        formatter = jsonlogger.JsonFormatter(
        LOG_FORMAT,
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

        handler.setFormatter(formatter)
        handler.addFilter(ContextFilter())

        root_logger.addHandler(handler)