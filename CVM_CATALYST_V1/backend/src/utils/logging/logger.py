"""Structured Logging Configuration"""
import logging
import json
from datetime import UTC, datetime
from src.core.config.settings import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def configure_logging():
    logger = logging.getLogger("cvm_catalyst")
    logger.setLevel(settings.LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)
    
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
