"""
Service Recommandation
FastAPI + Machine Learning (SVD / KNN)

Ce service nous permet de :
  1. Charge un modèle ML pré-entraîné (model.pkl)
  2. Expose des recommandations personnalisées par utilisateur
  3. Permet de ré-entraîner le modèle à la demande

Endpoints :
  GET  /                            info du service
  GET  /health                       santé du service
  GET  /recommendations/{user_id}    livres recommandés
  POST /train                        ré-entraîner le modèle
  GET  /model/info                   infos sur le modèle chargé
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import recommendations, training, health
from model.loader import ModelLoader

#  Configuration du logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


#  Chargement du modèle au démarrage 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan : code exécuté au démarrage et à l'arrêt.
    On charge le modèle ML une seule fois au démarrage.
    """
    logger.info(" Démarrage du service Recommandation...")

    model_path = os.environ.get("MODEL_PATH", "/models/model.pkl")
    data_path  = os.environ.get("DATA_PATH", "/data/loans_clean.csv")

    loader = ModelLoader(model_path=model_path, data_path=data_path)
    app.state.model_loader = loader
    app.state.model_path   = model_path
    app.state.data_path    = data_path

    loaded = loader.load()
    if loaded:
        logger.info(" Modèle ML chargé avec succès.")
    else:
        logger.warning(" Aucun modèle trouvé. Lance POST /train pour entraîner.")

    yield  # ← L'application tourne ici

    logger.info(" Arrêt du service Recommandation.")


# Création de l'application FastAPI 
app = FastAPI(
    title="DIT Bibliothèque — Service Recommandation",
    description="API de recommandation de livres basée sur l'historique des emprunts.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (autoriser les requêtes depuis React) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(health.router,           tags=["Santé"])
app.include_router(recommendations.router,  tags=["Recommandations"])
app.include_router(training.router,         tags=["Entraînement"])


@app.get("/", tags=["Info"])
def root():
    return {
        "service": "DIT Bibliothèque — Recommandation",
        "version": "1.0.0",
        "endpoints": {
            "health":          "GET  /health",
            "recommendations": "GET  /recommendations/{user_id}",
            "train":           "POST /train",
            "model_info":      "GET  /model/info",
        }
    }