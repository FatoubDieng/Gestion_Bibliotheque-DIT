"""
— Route Health Check
GET /health = vérifier l'état du service
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    status:      str
    service:     str
    modele_charge: bool
    modele_type:   str | None
    timestamp:   str


@router.get("/health", response_model=HealthResponse, summary="Vérifier l'état du service")
def health_check(request: Request):
    """
    Retourne l'état de santé du service.
    Utile pour Docker Compose healthcheck et monitoring.
    """
    loader = request.app.state.model_loader

    return HealthResponse(
        status="ok",
        service="reco-api",
        modele_charge=loader.is_loaded(),
        modele_type=loader.model_type,
        timestamp=datetime.now().isoformat()
    )