"""
train.py
Entraîne SVD ou KNN → model.pkl
Lit les paramètres depuis params.yaml
"""
import pandas as pd
import numpy as np
import joblib
import os
import sys
import yaml
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors

INPUT_PATH  = os.path.join('ml', 'data', 'loans_clean.csv')
OUTPUT_PATH = os.path.join('ml', 'models', 'model.pkl')


class SVDModel:
    def __init__(self, n_components=10):
        self.n_components  = n_components
        self.svd           = None
        self.user_matrix   = None
        self.reconstructed = None
        self.user_ids      = []
        self.book_ids      = []
        self.user_index    = {}
        self.book_index    = {}

    def fit(self, df):
        print(f"  → Construction matrice User×Livre...")
        self.user_ids   = sorted(df['user_id'].unique().tolist())
        self.book_ids   = sorted(df['book_id'].unique().tolist())
        self.user_index = {u: i for i, u in enumerate(self.user_ids)}
        self.book_index = {b: i for i, b in enumerate(self.book_ids)}
        n_u = len(self.user_ids)
        n_b = len(self.book_ids)
        self.user_matrix = np.zeros((n_u, n_b))
        for _, row in df.iterrows():
            self.user_matrix[self.user_index[row['user_id']]][self.book_index[row['book_id']]] = row['rating']
        n_comp = min(self.n_components, n_b - 1, n_u - 1)
        self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
        factors  = self.svd.fit_transform(self.user_matrix)
        self.reconstructed = np.dot(factors, self.svd.components_)
        print(f"  → Matrice {n_u}×{n_b} | {n_comp} composants latents")

    def predict(self, user_id, n_recommendations=5):
        if user_id not in self.user_index:
            return []
        u_idx  = self.user_index[user_id]
        scores = self.reconstructed[u_idx]
        deja   = {self.book_ids[i] for i, s in enumerate(self.user_matrix[u_idx]) if s > 0}
        recos  = [
            {'book_id': self.book_ids[i], 'score': round(float(s), 4)}
            for i, s in enumerate(scores)
            if self.book_ids[i] not in deja
        ]
        return sorted(recos, key=lambda x: x['score'], reverse=True)[:n_recommendations]


class KNNModel:
    def __init__(self, n_neighbors=5):
        self.n_neighbors = n_neighbors
        self.knn         = None
        self.user_matrix = None
        self.user_ids    = []
        self.book_ids    = []
        self.user_index  = {}
        self.book_index  = {}

    def fit(self, df):
        print(f"  → Construction matrice User×Livre...")
        self.user_ids   = sorted(df['user_id'].unique().tolist())
        self.book_ids   = sorted(df['book_id'].unique().tolist())
        self.user_index = {u: i for i, u in enumerate(self.user_ids)}
        self.book_index = {b: i for i, b in enumerate(self.book_ids)}
        n_u = len(self.user_ids)
        n_b = len(self.book_ids)
        self.user_matrix = np.zeros((n_u, n_b))
        for _, row in df.iterrows():
            self.user_matrix[self.user_index[row['user_id']]][self.book_index[row['book_id']]] = row['rating']
        k = min(self.n_neighbors, n_u)
        self.knn = NearestNeighbors(n_neighbors=k, metric='cosine', algorithm='brute')
        self.knn.fit(self.user_matrix)
        print(f"  → {n_u} utilisateurs | k={k} voisins")

    def predict(self, user_id, n_recommendations=5):
        if user_id not in self.user_index:
            return []
        u_idx  = self.user_index[user_id]
        vector = self.user_matrix[u_idx].reshape(1, -1)
        distances, indices = self.knn.kneighbors(vector)
        deja   = {self.book_ids[i] for i, s in enumerate(self.user_matrix[u_idx]) if s > 0}
        scores = {}
        for n_idx, dist in zip(indices[0][1:], distances[0][1:]):
            sim = 1 - dist
            for b_idx, rating in enumerate(self.user_matrix[n_idx]):
                if rating > 0:
                    bid = self.book_ids[b_idx]
                    if bid not in deja:
                        scores[bid] = scores.get(bid, 0) + rating * sim
        recos = [{'book_id': b, 'score': round(s, 4)} for b, s in scores.items()]
        return sorted(recos, key=lambda x: x['score'], reverse=True)[:n_recommendations]


def main():
    # ── Lire params.yaml 
    with open('params.yaml') as f:
        params = yaml.safe_load(f)

    algo         = params['train']['algo']
    n_components = params['train']['n_components']
    n_neighbors  = params['train']['n_neighbors']

    print("=" * 50)
    print(f"  Étape 2 : Entraînement ({algo})")
    print("=" * 50)

    # ── Charger les données 
    if not os.path.exists(INPUT_PATH):
        print(f" Fichier introuvable : {INPUT_PATH}")
        sys.exit(1)

    df = pd.read_csv(INPUT_PATH)
    print(f" Données chargées : {len(df)} lignes")

    # ── Split train / test
    if len(df) >= 10:
        df_train, _ = train_test_split(df, test_size=0.2, random_state=42)
    else:
        df_train = df

    print(f"   Train : {len(df_train)}")

    # ── Créer et entraîner le modèle 
    print(f"\n Entraînement {algo}...")

    if algo == 'SVD':
        modele = SVDModel(n_components=n_components)
    elif algo == 'KNN':
        modele = KNNModel(n_neighbors=n_neighbors)
    else:
        print(f"Algorithme inconnu : {algo}")
        sys.exit(1)

    modele.fit(df_train)

    #  Sauvegarder model.pkl 
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    payload = {
        'model':      modele,
        'model_type': algo,
        'n_users':    len(df['user_id'].unique()),
        'n_items':    len(df['book_id'].unique()),
        'trained_at': datetime.now().isoformat(),
        'params':     {'n_components': n_components, 'n_neighbors': n_neighbors}
    }

    joblib.dump(payload, OUTPUT_PATH)
    print(f"\n Modèle sauvegardé : {OUTPUT_PATH}")
    print("=" * 50)
    print("Entraînement terminé !")


if __name__ == '__main__':
    main()