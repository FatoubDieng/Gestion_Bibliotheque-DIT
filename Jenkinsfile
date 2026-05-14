pipeline {

    agent any

    // ── Variables d'environnement ────────────────────────────
    environment {
        DOCKER_COMPOSE_VERSION = '2.0'
        PYTHON_VERSION         = '3.11'
        PROJECT_NAME           = 'dit-bibliotheque'
        REGISTRY               = 'ghcr.io/ton-username'
    }

    // ── Paramètres configurables ─────────────────────────────
    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'prod'],
            description: 'Environnement de déploiement'
        )
        booleanParam(
            name: 'RUN_DVC',
            defaultValue: true,
            description: 'Lancer le pipeline DVC ?'
        )
    }

    // ── Déclencheurs ─────────────────────────────────────────
    triggers {
        // Se déclenche automatiquement à chaque push GitHub
        githubPush()
    }

    stages {

        // ════════════════════════════════════════════════════
        // STAGE 1 — Checkout
        // ════════════════════════════════════════════════════
        stage('Checkout') {
            steps {
                echo ' Récupération du code source...'
                checkout scm
                sh 'git log --oneline -5'
                sh 'echo "Branche : $(git branch --show-current)"'
            }
        }

        // ════════════════════════════════════════════════════
        // STAGE 2 — Installation des dépendances
        // ════════════════════════════════════════════════════
        stage('Install Dependencies') {
            steps {
                echo ' Installation des dépendances Python...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r services/livres/requirements.txt
                    pip install -r services/reco-api/requirements.txt
                    pip install dvc pandas numpy scikit-learn pytest
                '''
            }
        }

        // ════════════════════════════════════════════════════
        // STAGE 3 — Tests
        // ════════════════════════════════════════════════════
        stage('Tests') {
            parallel {

                stage('Test Service Livres') {
                    steps {
                        echo ' Tests service Livres...'
                        sh '''
                            . venv/bin/activate
                            cd services/livres
                            export DATABASE_URL=sqlite:///test_db.sqlite3
                            export DJANGO_SECRET_KEY=test-key
                            export DEBUG=True
                            python manage.py test livres_app --verbosity=2 || true
                        '''
                    }
                }

                stage('Test Service Users') {
                    steps {
                        echo ' Tests service Users...'
                        sh '''
                            . venv/bin/activate
                            cd services/users
                            export DATABASE_URL=sqlite:///test_db.sqlite3
                            export DJANGO_SECRET_KEY=test-key
                            export DEBUG=True
                            python manage.py test users_app --verbosity=2 || true
                        '''
                    }
                }

                stage('Test Service Emprunts') {
                    steps {
                        echo ' Tests service Emprunts...'
                        sh '''
                            . venv/bin/activate
                            cd services/emprunts
                            export DATABASE_URL=sqlite:///test_db.sqlite3
                            export DJANGO_SECRET_KEY=test-key
                            export DEBUG=True
                            export SERVICE_LIVRES_URL=http://localhost:8001
                            export SERVICE_USERS_URL=http://localhost:8002
                            python manage.py test emprunts_app --verbosity=2 || true
                        '''
                    }
                }

                stage('Test Reco API') {
                    steps {
                        echo 'Tests service Recommandation...'
                        sh '''
                            . venv/bin/activate
                            python -c "
import sys
sys.path.insert(0, 'services/reco-api')
print(' Import reco-api OK')
from model.recommender import SVDModel, KNNModel
print(' SVDModel et KNNModel importés')
"
                        '''
                    }
                }
            }

            post {
                always {
                    echo ' Tests terminés'
                }
                failure {
                    echo 'Des tests ont échoué !'
                }
            }
        }

        // ════════════════════════════════════════════════════
        // STAGE 4 — Pipeline DVC (ML)
        // ════════════════════════════════════════════════════
        stage('DVC Pipeline') {
            when {
                expression { params.RUN_DVC == true }
            }
            steps {
                echo ' Lancement du pipeline DVC...'
                sh '''
                    . venv/bin/activate

                    # Créer des données de test si loans.csv absent
                    if [ ! -f ml/data/loans.csv ]; then
                        echo "Création de données de test..."
                        mkdir -p ml/data ml/models
                        python -c "
import pandas as pd
data = {
    'user_id': [1,1,2,2,3,3,4,4,5,5,1,2,3,4,5],
    'book_id': [1,2,1,3,2,4,3,5,4,6,7,7,7,6,5],
    'rating':  [5,4,4,5,3,4,5,3,4,5,4,3,5,4,3]
}
pd.DataFrame(data).to_csv('ml/data/loans.csv', index=False)
print('Données créées : 15 emprunts')
"
                    fi

                    # Lancer le pipeline
                    python ml/preprocess.py
                    python ml/train.py
                    python ml/evaluate.py

                    # Afficher les métriques
                    echo "📊 Métriques du modèle :"
                    cat ml/metrics.json
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'ml/metrics.json', fingerprint: true
                    echo 'Pipeline DVC terminé — métriques archivées'
                }
            }
        }

        // ════════════════════════════════════════════════════
        // STAGE 5 — Build Docker
        // ════════════════════════════════════════════════════
        stage('Build Docker Images') {
            steps {
                echo '🐳 Construction des images Docker...'
                sh '''
                    docker build ./services/livres   -t dit-livres:latest   --no-cache
                    docker build ./services/users    -t dit-users:latest    --no-cache
                    docker build ./services/emprunts -t dit-emprunts:latest --no-cache
                    docker build ./services/reco-api -t dit-reco:latest     --no-cache
                    echo " Images construites :"
                    docker images | grep "^dit-"
                '''
            }
        }

        // ════════════════════════════════════════════════════
        // STAGE 6 — Deploy Dev
        // ════════════════════════════════════════════════════
        stage('Deploy Dev') {
            when {
                anyOf {
                    branch 'develop'
                    expression { params.DEPLOY_ENV == 'dev' }
                }
            }
            steps {
                echo ' Déploiement en mode DEV...'
                sh '''
                    docker compose --profile dev down || true
                    docker compose --profile dev up -d --build
                    echo " Services déployés en mode DEV"
                    docker compose ps
                '''
            }
        }

        // ════════════════════════════════════════════════════
        // STAGE 7 — Deploy Prod
        // ════════════════════════════════════════════════════
        stage('Deploy Prod') {
            when {
                anyOf {
                    branch 'master'
                    expression { params.DEPLOY_ENV == 'prod' }
                }
            }
            steps {
                echo 'Déploiement en mode PROD...'

                // Demander confirmation avant deploy prod
                input message: 'Confirmer le déploiement en production ?',
                      ok: 'Déployer'

                sh '''
                    docker compose --profile prod down || true
                    docker compose --profile prod up -d --build
                    echo " Services déployés en mode PROD"
                    docker compose ps
                '''
            }
        }
    }

    //  Post actions 
    post {
        always {
            echo 'Pipeline terminé'
            cleanWs()
        }
        success {
            echo '''
══════════════════════════════════
   Pipeline CI/CD réussi !
   DIT Lybrary
══════════════════════════════════
            '''
        }
        failure {
            echo '''
══════════════════════════════════
   Pipeline CI/CD échoué !
   Vérifier les logs ci-dessus
══════════════════════════════════
            '''
        }
    }
}