from fastapi import FastAPI
from app.core.config import settings
from app.api import webhook

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION
)

app.include_router(webhook.router)

@app.get("/")
def read_root():
    return {"message": "Remar Chatbot API is running"}
