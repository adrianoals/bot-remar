from fastapi import FastAPI
from app.core.config import settings
from app.api import webhook
import logging

# Configurar logging para ver tudo no console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION
)

app.include_router(webhook.router)

@app.get("/")
def read_root():
    return {"message": "Remar Chatbot API is running"}

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Aplicação iniciada - Logging ativado")
