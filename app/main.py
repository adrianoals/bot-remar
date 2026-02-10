import logging
import json
import os
import sys
from datetime import datetime, timezone
from fastapi import FastAPI
from app.api import webhook
from app.core.config import settings


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    use_json = os.getenv("LOG_JSON", "0") == "1"

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    if use_json:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
        )
    root.addHandler(handler)


configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION
)

app.include_router(webhook.router)

@app.get("/")
def read_root():
    return {"message": "Remar Chatbot API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.on_event("startup")
async def startup_event():
    logger.info("Aplicacao iniciada")
