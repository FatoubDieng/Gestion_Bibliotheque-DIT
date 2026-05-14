FROM python:3.11-slim

#  Utilisateur non-root 
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Dépendances système 
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY . .

# Dossier export ML 
RUN mkdir -p /ml_data && chown -R appuser:appuser /app /ml_data

# Utilisateur non-root 
USER appuser

# Port exposé 
EXPOSE 8003

# Lancement 
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8003", "--workers", "2"]