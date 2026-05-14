# Dockerfile — Service Recommandation (FastAPI + ML)
# Port : 8004
# Multi-stage build :
#   Stage 1 (builder) : installe les dépendances lourdes
#   Stage 2 (runtime) : image finale légère
# STAGE 1 — Builder
# Installe toutes les dépendances Python (numpy, scikit-learn...)
# Cette image est temporaire et ne sera pas dans l'image finale
FROM python:3.11-slim AS builder
WORKDIR /build

# Dépendances système pour compiler numpy/scipy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Installer les packages dans /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

# Utilisateur non-root 
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copier SEULEMENT les packages installés depuis le builder 
COPY --from=builder /install /usr/local

# Dossiers pour modèle et données 
RUN mkdir -p /ml_models /ml_data \
    && chown -R appuser:appuser /ml_models /ml_data /app

# Code source 
COPY --chown=appuser:appuser . .

# Variable d'environnement Python 
ENV PYTHONPATH=/app

# Utilisateur non-root 
USER appuser

# Port exposé 
EXPOSE 8004

# Lancement 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "1"]