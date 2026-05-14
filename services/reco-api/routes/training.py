"""
DIT Bibliothèque — Route Entraînement
POST /train → ré-entraîner le modèle ML
"""
import logging
import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sklearn.model_selection import train_test_split
from typing import Optional

from model.recommender import SVDRecommender, KNNRecommender

logger = logging.getLogger(__name__)
router = APIRouter()

class TrainRequest(BaseModel):
    """Paramètres optionnels pour l'entraînement"""
    algorithme:    str   = "SVD"    # "SVD" ou "KNN"
    n_components:  int   = 10       # Pour SVD : nombre de composants latents
    n_neighbors:   int   = 5        # Pour KNN : nombre de voisins
    test_size:     float = 0.2      # Proportion du jeu de test (0.0 à 0.5)


class TrainResponse(BaseModel):
    """Réponse après entraînement"""
    succes:       bool
    message:      str
    algorithme:   str
    n_users:      int
    n_items:      int
    metrics:      dict
    model_path:   str


@router.post(
    "/train",
    response_model=TrainResponse,
    summary="Entraîner ou ré-entraîner le modèle ML"
)
def train_model(request: Request, params: TrainRequest = TrainRequest()):
    """
    ## Entraînement du modèle de recommandation

    Charge les données depuis `loans_clean.csv`,
    entraîne le modèle choisi (SVD ou KNN),
    évalue ses performances et sauvegarde `model.pkl`.

    ### Algorithmes disponibles :
    - **SVD** : Décomposition en valeurs singulières (recommandé)
    - **KNN** : K plus proches voisins

    ### Exemple de body :
    ```json
    {
        "algorithme": "SVD",
        "n_components": 15,
        "test_size": 0.2
    }
    ```
    """
    loader    = request.app.state.model_loader
    data_path = request.app.state.data_path

    # Étape 1 : Charger les données 
    if not os.path.exists(data_path):
        raise HTTPException(
            status_code=404,
            detail=f"Fichier de données introuvable : {data_path}. "
                   f"Lance d'abord GET /api/emprunts/export-csv/ sur le service Emprunts."
        )

    try:
        df = pd.read_csv(data_path)
        logger.info(f"Données chargées : {len(df)} lignes depuis {data_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture CSV : {str(e)}")

    #  Étape 2 : Vérifier les colonnes 
    colonnes_requises = ['user_id', 'book_id', 'rating']
    manquantes = [c for c in colonnes_requises if c not in df.columns]
    if manquantes:
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes dans le CSV : {manquantes}. "
                   f"Colonnes présentes : {list(df.columns)}"
        )

    if len(df) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Pas assez de données pour entraîner ({len(df)} lignes). Minimum : 5."
        )

    # Étape 3 : Diviser en train / test 
    test_size = min(params.test_size, 0.4)
    if len(df) < 10:
        df_train, df_test = df, df   # Trop peu de données → même jeu
    else:
        df_train, df_test = train_test_split(
            df, test_size=test_size, random_state=42
        )

    logger.info(f"Train: {len(df_train)} | Test: {len(df_test)}")

    #  Étape 4 : Créer et entraîner le modèle 
    algo = params.algorithme.upper()

    try:
        if algo == "SVD":
            modele = SVDRecommender(n_components=params.n_components)
            modele.fit(df_train)
        elif algo == "KNN":
            modele = KNNRecommender(n_neighbors=params.n_neighbors)
            modele.fit(df_train)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Algorithme '{algo}' inconnu. Choisir 'SVD' ou 'KNN'."
            )
    except Exception as e:
        logger.error(f"Erreur entraînement : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur entraînement : {str(e)}")

    # Étape 5 : Évaluer le modèle 
    metrics = modele.evaluate(df_test)
    logger.info(f"Métriques : RMSE={metrics.get('rmse')} | MAE={metrics.get('mae')}")

    # Étape 6 : Sauvegarder le modèle
    n_users = len(df['user_id'].unique())
    n_items = len(df['book_id'].unique())

    loader.save(
        model=modele,
        model_type=algo,
        metrics=metrics,
        n_users=n_users,
        n_items=n_items
    )

    return TrainResponse(
        succes=True,
        message=f"Modèle {algo} entraîné avec succès sur {len(df_train)} emprunts.",
        algorithme=algo,
        n_users=n_users,
        n_items=n_items,
        metrics=metrics,
        model_path=loader.model_path
    )