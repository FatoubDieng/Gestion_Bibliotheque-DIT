"""
Model Loader
Gère le chargement, la sauvegarde et les infos du modèle ML.
"""
import os
import logging
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Responsable du cycle de vie du modèle ML :
      - Charger model.pkl depuis le disque
      - Sauvegarder le modèle après entraînement
      - Fournir les métadonnées du modèle

    Le modèle chargé peut être :
      - SVDModel  (filtrage collaboratif par décomposition matricielle)
      - KNNModel  (k plus proches voisins)
    """

    def __init__(self, model_path: str, data_path: str):
        self.model_path  = model_path
        self.data_path   = data_path
        self.model       = None          # Le modèle ML lui-même
        self.model_type  = None          # "SVD" ou "KNN"
        self.loaded_at   = None          # Timestamp du chargement
        self.metrics     = {}            # RMSE, MAE du modèle
        self.n_users     = 0             # Nombre d'utilisateurs connus
        self.n_items     = 0             # Nombre de livres connus

    def load(self) -> bool:
        """
        Charge le modèle depuis model.pkl.
        Retourne True si succès, False si le fichier n'existe pas.
        """
        if not os.path.exists(self.model_path):
            logger.warning(f"Fichier modèle introuvable : {self.model_path}")
            return False

        try:
            data = joblib.load(self.model_path)

            # On sauvegarde le modèle et ses métadonnées
            self.model      = data.get("model")
            self.model_type = data.get("model_type", "inconnu")
            self.metrics    = data.get("metrics", {})
            self.n_users    = data.get("n_users", 0)
            self.n_items    = data.get("n_items", 0)
            self.loaded_at  = datetime.now().isoformat()

            logger.info(f"Modèle '{self.model_type}' chargé — {self.n_users} users, {self.n_items} livres")
            return True

        except Exception as e:
            logger.error(f"Erreur chargement modèle : {e}")
            return False

    def save(self, model, model_type: str, metrics: dict, n_users: int, n_items: int):
        """
        Sauvegarde le modèle entraîné dans model.pkl.
        """
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        data = {
            "model":      model,
            "model_type": model_type,
            "metrics":    metrics,
            "n_users":    n_users,
            "n_items":    n_items,
            "trained_at": datetime.now().isoformat(),
        }

        joblib.dump(data, self.model_path)

        # Mettre à jour l'état interne
        self.model      = model
        self.model_type = model_type
        self.metrics    = metrics
        self.n_users    = n_users
        self.n_items    = n_items
        self.loaded_at  = datetime.now().isoformat()

        logger.info(f"Modèle '{model_type}' sauvegardé dans {self.model_path}")

    def is_loaded(self) -> bool:
        return self.model is not None

    def get_info(self) -> dict:
        return {
            "chargé":      self.is_loaded(),
            "type":        self.model_type,
            "chargé_le":   self.loaded_at,
            "n_users":     self.n_users,
            "n_items":     self.n_items,
            "metrics":     self.metrics,
            "model_path":  self.model_path,
        }