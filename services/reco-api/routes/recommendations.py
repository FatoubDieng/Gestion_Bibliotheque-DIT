"""
— Route Recommandations
GET /recommendations/{user_id}
"""
import logging
import requests
import os
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


SERVICE_LIVRES_URL = os.environ.get("SERVICE_LIVRES_URL", "http://service-livres-dev:8001")


class LivreRecommande(BaseModel):
    """Structure d'un livre recommandé dans la réponse"""
    book_id: int
    score:   float
    titre:   Optional[str] = None
    auteur:  Optional[str] = None
    categorie: Optional[str] = None


class RecommandationResponse(BaseModel):
    user_id:         int
    nb_recommandations: int
    algorithme:      str
    recommandations: list[LivreRecommande]


def enrichir_avec_details(recommandations: list[dict]) -> list[dict]:
    """
    Enrichit les recommandations avec les détails des livres
    en appelant le service Livres.
    
    Si le service Livres est indisponible, retourne les reco sans détails.
    """
    enrichies = []
    for reco in recommandations:
        book_id = reco["book_id"]
        details = {"titre": None, "auteur": None, "categorie": None}
        try:
            resp = requests.get(
                f"{SERVICE_LIVRES_URL}/api/livres/{book_id}/",
                timeout=3
            )
            if resp.status_code == 200:
                livre = resp.json()
                details = {
                    "titre":     livre.get("titre"),
                    "auteur":    livre.get("auteur"),
                    "categorie": livre.get("categorie"),
                }
        except requests.exceptions.RequestException:
            pass  # Service Livres indisponible → on continue sans détails

        enrichies.append({**reco, **details})
    return enrichies


@router.get(
    "/recommendations/{user_id}",
    response_model=RecommandationResponse,
    summary="Obtenir les recommandations pour un utilisateur"
)
def get_recommendations(
    user_id: int,
    request: Request,
    n: int = Query(default=5, ge=1, le=20, description="Nombre de recommandations (1-20)"),
    enrichir: bool = Query(default=True, description="Enrichir avec les détails des livres")
):
    """
    ## Recommandations personnalisées

    Retourne les **N livres les plus susceptibles de plaire** à l'utilisateur
    en se basant sur son historique d'emprunts et celui des utilisateurs similaires.

    - **user_id** : ID de l'utilisateur
    - **n** : nombre de recommandations (défaut: 5, max: 20)
    - **enrichir** : ajouter les détails des livres (titre, auteur)
    """
    loader = request.app.state.model_loader

    #  Vérifier que le modèle est chargé 
    if not loader.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Modèle ML non disponible. Lancez POST /train pour entraîner le modèle."
        )

    # Générer les recommandations 
    try:
        recommandations = loader.model.predict(user_id, n_recommendations=n)
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction pour user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {str(e)}")

    # Cas : utilisateur inconnu du modèle 
    if not recommandations:
        logger.info(f"User {user_id} inconnu → retour des livres populaires")
        # Fallback : retourner les livres les plus empruntés
        return RecommandationResponse(
            user_id=user_id,
            nb_recommandations=0,
            algorithme=loader.model_type or "inconnu",
            recommandations=[]
        )

    #  Enrichir avec les détails des livres
    if enrichir:
        recommandations = enrichir_avec_details(recommandations)

    return RecommandationResponse(
        user_id=user_id,
        nb_recommandations=len(recommandations),
        algorithme=loader.model_type,
        recommandations=[LivreRecommande(**r) for r in recommandations]
    )


@router.get(
    "/model/info",
    summary="Informations sur le modèle chargé"
)
def model_info(request: Request):
    """Retourne les métadonnées du modèle ML actuellement chargé."""
    loader = request.app.state.model_loader
    return loader.get_info()