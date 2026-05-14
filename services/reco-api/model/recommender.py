"""
-Algorithmes de Recommandation
Implémentation de SVD et KNN pour le filtrage collaboratif.

Concept du Filtrage Collaboratif :
  On construit une matrice Utilisateurs × Livres
  où chaque cellule = note donnée par l'utilisateur au livre.

"""
import logging
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class SVDRecommender:
    """
    Recommandation par SVD (Singular Value Decomposition).

    Principe :
      1. Construire la matrice user × livre
      2. Décomposer avec SVD en matrices latentes
      3. Reconstruire la matrice complète (avec les 0 remplis)
      4. Pour un user → prendre les livres avec les meilleures scores
         parmi ceux qu'il n'a PAS encore empruntés
    """

    def __init__(self, n_components: int = 10):
        self.n_components   = n_components
        self.svd            = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_matrix    = None   # Matrice user × livre originale
        self.reconstructed  = None   # Matrice reconstruite après SVD
        self.user_ids       = []     # Liste des IDs utilisateurs
        self.book_ids       = []     # Liste des IDs livres
        self.user_index     = {}     # user_id → index dans la matrice
        self.book_index     = {}     # book_id → index dans la matrice

    def fit(self, df: pd.DataFrame):
        """
        Entraîne le modèle SVD sur le DataFrame des emprunts.

        df doit avoir les colonnes : user_id, book_id, rating
        """
        logger.info(f"Entraînement SVD sur {len(df)} emprunts...")

        # Construire la matrice user × livre 
        self.user_ids  = sorted(df['user_id'].unique().tolist())
        self.book_ids  = sorted(df['book_id'].unique().tolist())
        self.user_index = {uid: i for i, uid in enumerate(self.user_ids)}
        self.book_index = {bid: i for i, bid in enumerate(self.book_ids)}

        # Créer la matrice (remplie de 0 par défaut)
        n_users = len(self.user_ids)
        n_books = len(self.book_ids)
        self.user_matrix = np.zeros((n_users, n_books))

        # Remplir avec les notes réelles
        for _, row in df.iterrows():
            u_idx = self.user_index[row['user_id']]
            b_idx = self.book_index[row['book_id']]
            self.user_matrix[u_idx][b_idx] = row['rating']

        # Appliquer SVD
        # Réduire les composants si pas assez de livres
        n_components = min(self.n_components, n_books - 1, n_users - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)

        # Transformer et reconstruire
        user_factors    = self.svd.fit_transform(self.user_matrix)
        book_factors    = self.svd.components_
        self.reconstructed = np.dot(user_factors, book_factors)

        logger.info(f"SVD entraîné — matrice {n_users}×{n_books}, {n_components} composants")

    def predict(self, user_id: int, n_recommendations: int = 5) -> list[dict]:
        """
        Génère les N meilleures recommandations pour un utilisateur.
        Exclut les livres déjà empruntés par cet utilisateur.
        """
        if user_id not in self.user_index:
            logger.warning(f"User {user_id} inconnu du modèle.")
            return []

        u_idx = self.user_index[user_id]

        # Scores prédits pour tous les livres
        scores = self.reconstructed[u_idx]

        # Livres déjà empruntés par cet utilisateur (score > 0 dans la matrice originale)
        deja_empruntes = set(
            self.book_ids[i]
            for i, s in enumerate(self.user_matrix[u_idx])
            if s > 0
        )

        # Construire la liste des recommandations
        recommandations = []
        for b_idx, score in enumerate(scores):
            book_id = self.book_ids[b_idx]
            if book_id not in deja_empruntes:
                recommandations.append({
                    "book_id": book_id,
                    "score":   round(float(score), 4)
                })

        # Trier par score décroissant et prendre les N meilleurs
        recommandations.sort(key=lambda x: x['score'], reverse=True)
        return recommandations[:n_recommendations]

    def evaluate(self, df_test: pd.DataFrame) -> dict:
        """Calcule RMSE et MAE sur un jeu de test."""
        y_true, y_pred = [], []

        for _, row in df_test.iterrows():
            if row['user_id'] in self.user_index and row['book_id'] in self.book_index:
                u_idx = self.user_index[row['user_id']]
                b_idx = self.book_index[row['book_id']]
                y_pred.append(self.reconstructed[u_idx][b_idx])
                y_true.append(row['rating'])

        if not y_true:
            return {"rmse": None, "mae": None}

        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae  = float(mean_absolute_error(y_true, y_pred))
        return {"rmse": round(rmse, 4), "mae": round(mae, 4)}


class KNNRecommender:
    """
    Recommandation par KNN (K-Nearest Neighbors).

    Principe :
      1. Construire la matrice user × livre
      2. Pour un user → trouver les K utilisateurs les plus similaires
      3. Recommander les livres qu'ils ont aimés
         mais que l'utilisateur cible n'a pas encore empruntés
    """

    def __init__(self, n_neighbors: int = 5):
        self.n_neighbors  = n_neighbors
        self.knn          = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            algorithm='brute'
        )
        self.user_matrix  = None
        self.user_ids     = []
        self.book_ids     = []
        self.user_index   = {}
        self.book_index   = {}

    def fit(self, df: pd.DataFrame):
        """Entraîne le modèle KNN."""
        logger.info(f"Entraînement KNN sur {len(df)} emprunts...")

        self.user_ids   = sorted(df['user_id'].unique().tolist())
        self.book_ids   = sorted(df['book_id'].unique().tolist())
        self.user_index = {uid: i for i, uid in enumerate(self.user_ids)}
        self.book_index = {bid: i for i, bid in enumerate(self.book_ids)}

        n_users = len(self.user_ids)
        n_books = len(self.book_ids)
        self.user_matrix = np.zeros((n_users, n_books))

        for _, row in df.iterrows():
            u_idx = self.user_index[row['user_id']]
            b_idx = self.book_index[row['book_id']]
            self.user_matrix[u_idx][b_idx] = row['rating']

        # Adapter n_neighbors si pas assez d'utilisateurs
        n_neighbors = min(self.n_neighbors, n_users)
        self.knn = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            algorithm='brute'
        )
        self.knn.fit(self.user_matrix)
        logger.info(f"KNN entraîné — {n_users} users, {n_books} livres, k={n_neighbors}")

    def predict(self, user_id: int, n_recommendations: int = 5) -> list[dict]:
        """Génère des recommandations via les voisins les plus proches."""
        if user_id not in self.user_index:
            logger.warning(f"User {user_id} inconnu du modèle.")
            return []

        u_idx = self.user_index[user_id]
        user_vector = self.user_matrix[u_idx].reshape(1, -1)

        # Trouver les K voisins les plus proches
        distances, indices = self.knn.kneighbors(user_vector)

        # Livres déjà empruntés par l'utilisateur cible
        deja_empruntes = set(
            self.book_ids[i]
            for i, s in enumerate(self.user_matrix[u_idx])
            if s > 0
        )

        # Agréger les scores des voisins
        scores = {}
        for neighbor_idx, distance in zip(indices[0][1:], distances[0][1:]):
            similarite = 1 - distance   # similarité cosinus
            neighbor_vector = self.user_matrix[neighbor_idx]

            for b_idx, rating in enumerate(neighbor_vector):
                if rating > 0:
                    book_id = self.book_ids[b_idx]
                    if book_id not in deja_empruntes:
                        scores[book_id] = scores.get(book_id, 0) + (rating * similarite)

        # Trier et retourner les N meilleurs
        recommandations = [
            {"book_id": bid, "score": round(score, 4)}
            for bid, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ]
        return recommandations[:n_recommendations]

    def evaluate(self, df_test: pd.DataFrame) -> dict:
        """Calcule RMSE et MAE sur un jeu de test."""
        y_true, y_pred = [], []

        for _, row in df_test.iterrows():
            if row['user_id'] in self.user_index and row['book_id'] in self.book_index:
                preds = self.predict(row['user_id'], n_recommendations=20)
                pred_score = next(
                    (p['score'] for p in preds if p['book_id'] == row['book_id']), 0
                )
                y_pred.append(pred_score)
                y_true.append(row['rating'])

        if not y_true:
            return {"rmse": None, "mae": None}

        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae  = float(mean_absolute_error(y_true, y_pred))
        return {"rmse": round(rmse, 4), "mae": round(mae, 4)}