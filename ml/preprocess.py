"""
Étape 1 preprocess.py

Rôle :
  - Lire loans.csv (export brut depuis le service Emprunts)
  - Nettoyer les données
  - Produire loans_clean.csv prêt pour l'entraînement

Usage :
  python preprocess.py

Appelé automatiquement par : dvc repro
"""

import pandas as pd
import numpy as np
import os
import sys

# Chemins des fichiers 
INPUT_PATH  = os.path.join('ml', 'data', 'loans.csv')
OUTPUT_PATH = os.path.join('ml', 'data', 'loans_clean.csv')


def charger_donnees(path: str) -> pd.DataFrame:
    """Charge le CSV brut des emprunts."""
    print(f"Chargement de {path}...")

    if not os.path.exists(path):
        print(f"Fichier introuvable : {path}")
        print("   → Lance d'abord : GET /api/emprunts/export-csv/ sur le service Emprunts")
        sys.exit(1)

    df = pd.read_csv(path)
    print(f"   {len(df)} lignes chargées")
    print(f"   Colonnes : {list(df.columns)}")
    return df


def nettoyer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoyage complet du DataFrame.

    Opérations :
      1. Supprimer les doublons
      2. Supprimer les lignes avec user_id ou book_id manquants
      3. Normaliser les ratings (entre 1 et 5)
      4. Supprimer les outliers de durée d'emprunt
      5. Convertir les types
    """
    print("\n Nettoyage des données...")
    initial = len(df)

    #  1. Supprimer les doublons 
    df = df.drop_duplicates()
    print(f"   Doublons supprimés     : {initial - len(df)}")

    #  2. Supprimer lignes incomplètes 
    avant = len(df)
    df = df.dropna(subset=['user_id', 'book_id'])
    print(f"   Lignes incomplètes     : {avant - len(df)}")

    # ── 3. Convertir les types 
    df['user_id'] = df['user_id'].astype(int)
    df['book_id'] = df['book_id'].astype(int)

    #  4. Normaliser les ratings 
    # Si rating manquant on le met 3 (neutre)
    df['rating'] = df['rating'].fillna(3)

    # Clipper entre 1 et 5
    avant = len(df)
    df['rating'] = df['rating'].clip(1, 5).astype(float)
    print(f"   Ratings normalisés     : entre 1 et 5")

    #  5. Supprimer les durées aberrantes
    if 'duree_jours' in df.columns:
        avant = len(df)
        df = df[df['duree_jours'] >= 0]          # pas de durée négative
        df = df[df['duree_jours'] <= 365]         # max 1 an
        print(f"   Durées aberrantes      : {avant - len(df)}")

    #  6. Garder seulement les colonnes utiles pour le ML 
    colonnes_ml = ['user_id', 'book_id', 'rating']
    if 'date_emprunt' in df.columns:
        colonnes_ml.append('date_emprunt')
    df = df[colonnes_ml]

    print(f"\n  Données propres : {len(df)} lignes (perdues : {initial - len(df)})")
    return df


def afficher_statistiques(df: pd.DataFrame):
    """Affiche des statistiques sur les données nettoyées."""
    print("\n Statistiques des données nettoyées :")
    print(f"   Utilisateurs uniques : {df['user_id'].nunique()}")
    print(f"   Livres uniques       : {df['book_id'].nunique()}")
    print(f"   Total emprunts       : {len(df)}")
    print(f"   Rating moyen         : {df['rating'].mean():.2f}")
    print(f"   Distribution ratings :")
    for note in [1, 2, 3, 4, 5]:
        count = (df['rating'] == note).sum()
        bar   = '█' * int(count / max(len(df), 1) * 30)
        print(f"     {note}⭐ {bar} ({count})")


def main():
    print("=" * 50)
    print("  DVC Pipeline — Étape 1 : Preprocessing")
    print("=" * 50)

    # Charger
    df = charger_donnees(INPUT_PATH)

    # Nettoyer
    df_clean = nettoyer_donnees(df)

    # Statistiques
    afficher_statistiques(df_clean)

    # Sauvegarder
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"\n Sauvegardé : {OUTPUT_PATH}")
    print("=" * 50)
    print(" Preprocessing terminé !")


if __name__ == '__main__':
    main()
