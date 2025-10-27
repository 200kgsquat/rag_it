from fastapi import APIRouter
from src.qabot.api.schemas import HealthResponse

health = APIRouter()


@health.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}
