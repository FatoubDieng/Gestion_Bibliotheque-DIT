"""
Étape 3 evaluate.py
Rôle :
  - Charger model.pkl
  - Calculer RMSE et MAE sur les données de test
  - Sauvegarder metrics.json (lu par : dvc metrics show)

Usage :
  python evaluate.py
Appelé automatiquement par : dvc repro
"""

 
import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
 
# Import des classes ML (nécessaire pour charger model.pkl) ─
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train import SVDModel, KNNModel
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

# Path
DATA_PATH    = os.path.join('ml', 'data',   'loans_clean.csv')
MODEL_PATH   = os.path.join('ml', 'models', 'model.pkl')
METRICS_PATH = os.path.join('ml', 'metrics.json')


def evaluer_svd(modele, df_test):
    """Évalue un modèle SVD sur le jeu de test."""
    y_true, y_pred = [], []

    for _, row in df_test.iterrows():
        uid = row['user_id']
        bid = row['book_id']

        if uid in modele.user_index and bid in modele.book_index:
            u_idx = modele.user_index[uid]
            b_idx = modele.book_index[bid]
            pred  = modele.reconstructed[u_idx][b_idx]
            y_pred.append(float(pred))
            y_true.append(float(row['rating']))

    return y_true, y_pred


def evaluer_knn(modele, df_test):
    """Évalue un modèle KNN sur le jeu de test."""
    y_true, y_pred = [], []

    for _, row in df_test.iterrows():
        uid = row['user_id']
        bid = row['book_id']

        if uid in modele.user_index and bid in modele.book_index:
            recos = modele.predict(uid, n_recommendations=50)
            score = next((r['score'] for r in recos if r['book_id'] == bid), 0.0)
            y_pred.append(float(score))
            y_true.append(float(row['rating']))

    return y_true, y_pred


def calculer_metriques(y_true, y_pred):
    """Calcule RMSE et MAE."""
    if not y_true:
        return {'rmse': None, 'mae': None, 'n_predictions': 0}

    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae  = float(mean_absolute_error(y_true, y_pred))

    return {
        'rmse':          round(rmse, 4),
        'mae':           round(mae, 4),
        'n_predictions': len(y_true),
        'rating_moyen':  round(float(np.mean(y_true)), 4),
    }


def main():
    print("=" * 50)
    print("  DVC Pipeline — Étape 3 : Évaluation")
    print("=" * 50)

    #  Charger le modèle 
    if not os.path.exists(MODEL_PATH):
        print(f" Modèle introuvable : {MODEL_PATH}")
        print("   → Lance d'abord train.py")
        sys.exit(1)

    print(f" Chargement du modèle : {MODEL_PATH}")
    payload     = joblib.load(MODEL_PATH)
    modele      = payload['model']
    model_type  = payload['model_type']
    print(f"   Algorithme : {model_type}")
    print(f"   Entraîné le : {payload.get('trained_at', '?')}")

    #  Charger les données de test 
    if not os.path.exists(DATA_PATH):
        print(f" Données introuvables : {DATA_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    if len(df) >= 10:
        _, df_test = train_test_split(df, test_size=0.2, random_state=42)
    else:
        df_test = df

    print(f"   Données de test : {len(df_test)} lignes")

    #  Évaluer selon le type de modèle 
    print(f"\n Calcul des métriques...")

    if model_type == 'SVD':
        y_true, y_pred = evaluer_svd(modele, df_test)
    else:
        y_true, y_pred = evaluer_knn(modele, df_test)

    metriques = calculer_metriques(y_true, y_pred)

    # Afficher les résultats 
    print(f"\n Résultats :")
    print(f"   RMSE            : {metriques['rmse']}")
    print(f"   MAE             : {metriques['mae']}")
    print(f"   Prédictions     : {metriques['n_predictions']}")
    print(f"   Rating moyen    : {metriques.get('rating_moyen')}")
    print()
    print("   RMSE = Root Mean Square Error (plus c'est bas, mieux c'est)")
    print("   MAE  = Mean Absolute Error    (plus c'est bas, mieux c'est)")

    # Sauvegarder metrics.json
    metrics_final = {
        'algorithme':    model_type,
        'rmse':          metriques['rmse'],
        'mae':           metriques['mae'],
        'n_predictions': metriques['n_predictions'],
        'n_users':       payload.get('n_users'),
        'n_items':       payload.get('n_items'),
        'trained_at':    payload.get('trained_at'),
    }

    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics_final, f, indent=2)

    print(f"\n Métriques sauvegardées : {METRICS_PATH}")
    print("=" * 50)
    print(" Évaluation terminée !")
    print()
    print("   Pour voir les métriques : dvc metrics show")
    print("   Pour comparer versions  : dvc metrics diff")


if __name__ == '__main__':
    main()
