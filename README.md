#  DIT Bibliothèque — Plateforme de Gestion Académique

> Système complet de gestion de bibliothèque universitaire avec recommandations IA  
> **Dakar Institute of Technology** — Projet Outils de Versioning

---

##  Table des Matières

- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation et Lancement](#installation-et-lancement)
- [Initialisation de la Base de Données](#initialisation-de-la-base-de-données)
- [Services et Endpoints](#services-et-endpoints)
- [Pipeline DVC](#pipeline-dvc)
- [Tests des Endpoints](#tests-des-endpoints)
- [Workflow Git](#workflow-git)

---

##  Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React)                  │
│              http://localhost:3000                  │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼───────┐ ┌──────────────┐
│   Livres     │ │   Users    │ │  Emprunts  │ │   Reco IA    │
│  Django      │ │  Django    │ │  Django    │ │  FastAPI+ML  │
│  :8001       │ │  :8002     │ │  :8003     │ │  :8004       │
└───────┬──────┘ └─────┬──────┘ └────┬───────┘ └──────────────┘
        └──────────────┴──────────────┘
                       │
              ┌────────▼────────┐
              │   PostgreSQL    │
              │     :5432       │cls
              └─────────────────┘
```

---

##  Prérequis

| Outil | Version minimale |
|---|---|
| Docker Desktop | 24.x |
| Docker Compose | 2.x |
| Python | 3.11+ |
| Git | 2.x |
| Node.js | 18+ |

---

##  Installation et Lancement

### 1. Cloner le projet

```bash
git clone https://github.com/FatoubDieng/Gestion_Bibliotheque-DIT.git
cd gestion_bibliotheques
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Modifier .env selon ton environnement
```

### 3. Lancer en mode développement (hot-reload)

```bash
docker compose --profile dev up --build
```

### 4. Lancer en mode production

```bash
docker compose --profile prod up --build
```

### 5. Vérifier que tout tourne

```bash
docker ps
```

Tu dois voir :
```
dit_postgres     Up (healthy)
dit_livres_dev   Up
dit_users_dev    Up
dit_emprunts_dev Up
dit_reco_dev     Up
dit_frontend_dev Up
```

---

##  Initialisation de la Base de Données

La base de données est **initialisée automatiquement** au premier démarrage via `init.sql`.

Elle contient :
- **48 livres** (informatique, littérature, data science...)
- **50 utilisateurs** (étudiants, professeurs, personnel)

### Appliquer les migrations Django

```bash
# Service Livres
docker exec dit_livres_dev python manage.py migrate --fake-initial

# Service Users
docker exec dit_users_dev python manage.py migrate --fake-initial

# Service Emprunts
docker exec dit_emprunts_dev python manage.py migrate --fake-initial
```

---

## Services et Endpoints

### Service Livres — Port 8001

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/livres/` | Lister tous les livres |
| POST | `/api/livres/` | Ajouter un livre |
| PUT | `/api/livres/{id}/` | Modifier un livre |
| DELETE | `/api/livres/{id}/` | Supprimer un livre |
| GET | `/api/livres/search/?q=python` | Recherche |
| GET | `/api/livres/disponibles/` | Livres disponibles |
| GET | `/api/health/` | Health check |

### Service Utilisateurs — Port 8002

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/users/` | Lister les utilisateurs |
| POST | `/api/users/` | Créer un utilisateur |
| GET | `/api/users/{id}/profil/` | Profil utilisateur |
| GET | `/api/users/par-type/?type=etudiant` | Filtrer par type |
| GET | `/api/users/statistiques/` | Statistiques |

### Service Emprunts — Port 8003

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/emprunts/emprunter/` | Emprunter un livre |
| POST | `/api/emprunts/{id}/retourner/` | Retourner un livre |
| GET | `/api/emprunts/historique/` | Historique |
| GET | `/api/emprunts/retards/` | Emprunts en retard |
| GET | `/api/emprunts/export-csv/` | Export pour ML |

### Service Recommandation — Port 8004

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/recommendations/{user_id}` | Recommandations |
| POST | `/train` | Entraîner le modèle |
| GET | `/model/info` | Infos du modèle |
| GET | `/health` | Health check |

---

##  Pipeline DVC

### Initialiser DVC

```bash
# Activer le venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# Initialiser
dvc init

#### 1. Configuration du remote Google Drive
Récupérez l'identifiant de votre dossier partagé Google Drive (la chaîne de caractères dans l'URL du dossier) et exécutez :

```bash
# Ajouter le remote Google Drive
dvc remote add -d gdrive_remote gdrive://VOTRE_ID_DOSSIER_GOOGLE_DRIVE

# Installer l'extension requise pour Google Drive
pip install "dvc[gdrive]"
```

#### 2. Partage et Récupération des données
Une fois configuré, les commandes restent identiques pour toute l'équipe :

```bash
# Pour envoyer les données/modèles sur Google Drive
dvc push

# Pour récupérer les données/modèles depuis Google Drive (après un git pull)
dvc pull
```

*Note : Lors du premier `dvc push` ou `dvc pull`, un lien s'affichera dans votre terminal pour vous authentifier avec votre compte Google.*

# Configurer le remote en local Si vous ne souhaitez pas utiliser Google Drive

dvc remote add -d myremote C:\Users\TON_NOM\Documents\dvc-storage


```

### Générer les données

```bash
# Exporter les emprunts depuis PostgreSQL
Invoke-WebRequest -Uri "http://localhost:8003/api/emprunts/export-csv/" -UseBasicParsing

# Copier vers ml/data/
docker cp dit_emprunts_dev:/ml_data/loans.csv ml\data\loans.csv

# Versionner avec DVC
dvc add ml/data/loans.csv
git add ml/data/loans.csv.dvc
git commit -m "data: ajout loans.csv"
```

### Lancer le pipeline

```bash
dvc repro
```

Le pipeline exécute 3 étapes :
```
loans.csv → preprocess.py → loans_clean.csv
                          → train.py → model.pkl
                                    → evaluate.py → metrics.json
```

### Voir les métriques

```bash
dvc metrics show
```

```
Path             mae     rmse
ml\metrics.json  3.45    3.81
```

### Comparer deux versions du modèle

```bash
# Changer params.yaml (algo: SVD → KNN)
dvc repro
dvc metrics diff HEAD~1
```

```
Metric    HEAD~1    workspace    Change
rmse      4.11      3.81         -0.30  
mae       4.06      3.45         -0.61  
```

### Pousser sur le remote

```bash
dvc push
```

---

##  Tests des Endpoints

### Windows (PowerShell)

```powershell
# Tester le service Livres
Invoke-WebRequest -Uri "http://localhost:8001/api/livres/" -UseBasicParsing

# Tester le service Users
Invoke-WebRequest -Uri "http://localhost:8002/api/users/" -UseBasicParsing

# Emprunter un livre
Invoke-WebRequest -Uri "http://localhost:8003/api/emprunts/emprunter/" `
  -Method POST -ContentType "application/json" `
  -Body '{"utilisateur_id": 1, "livre_id": 1}' -UseBasicParsing

# Obtenir des recommandations
Invoke-WebRequest -Uri "http://localhost:8004/recommendations/1" -UseBasicParsing

# Entraîner le modèle
Invoke-WebRequest -Uri "http://localhost:8004/train" `
  -Method POST -ContentType "application/json" `
  -Body '{"algorithme": "SVD", "n_components": 10}' -UseBasicParsing
```

### Linux / Mac

```bash
curl http://localhost:8001/api/livres/
curl http://localhost:8002/api/users/
curl -X POST http://localhost:8003/api/emprunts/emprunter/ \
  -H "Content-Type: application/json" \
  -d '{"utilisateur_id": 1, "livre_id": 1}'
```

---

##  Workflow Git

```
main
  └── develop
        ├── feature/livres
        ├── feature/users
        ├── feature/emprunts
        ├── feature/reco
        └── feature/frontend
```

### Commandes Git utilisées

```bash
# Créer une branche feature
git checkout develop
git checkout -b feature/livres

# Commiter
git add .
git commit -m "feat: ajout service livres"

# Merger dans develop
git checkout develop
git merge feature/livres

# Tagger une version
git tag -a v1.0.0 -m "Version 1.0.0 - Release initiale"
git push origin v1.0.0
```

---

##  Structure du Projet

```
gestion_bibliotheques/
├── services/
│   ├── livres/          ← Django (port 8001)
│   ├── users/           ← Django (port 8002)
│   ├── emprunts/        ← Django (port 8003)
│   └── reco-api/        ← FastAPI + ML (port 8004)
├── frontend/            ← React (port 3000)
├── ml/
│   ├── data/            ← loans.csv, loans_clean.csv
│   ├── models/          ← model.pkl
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── docker-compose.yml   ← Profils dev + prod
├── init.sql             ← Schéma + données initiales
├── dvc.yaml             ← Pipeline ML
├── params.yaml          ← Hyperparamètres
└── .env.example         ← Variables d'environnement
```

---

##  Auteur

**Fatou DIENG & Glossoa Desson Olivier Glindet**  
  
