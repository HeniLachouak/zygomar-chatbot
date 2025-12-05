# ========= Étape 1 : Build (léger) =========
FROM python:3.11-slim AS builder

WORKDIR /app

# Install seulement ce qu’il faut pour compiler (si besoin)
RUN pip install --upgrade pip

# Copie uniquement les dépendances d’abord (cache optimal)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ========= Étape 2 : Image finale ultra légère =========
FROM python:3.11-slim

WORKDIR /app

# Copie Python + dépendances installées depuis le builder
COPY --from=builder /root/.local /root/.local

# Ajoute le binaire pip installé localement au PATH
ENV PATH=/root/.local/bin:$PATH

# Copie le code de l’app
COPY chatbot_server.py .
COPY templates ./templates
COPY static ./static

# Variables d’environnement (valeurs par défaut, écrasées au run)
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose le port
EXPOSE 8000

# Utilise gunicorn en prod (meilleur que flask run)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "chatbot_server:app"]