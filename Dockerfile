FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the SBERT encoder into the image. Without this the container downloads
# ~90 MB from HuggingFace on every start, and cannot boot at all without
# internet. This layer only rebuilds when requirements.txt changes.
ENV HF_HOME=/app/hf-cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Backend modules (app, db, auth, models, training + utility scripts)
COPY *.py .

# Model weights and UI template data
COPY recruitment_model.pth .
COPY verified_templates.json .
COPY ui_templates.json .

# Holds the SQLite file; mount a volume here so accounts survive a rebuild
RUN mkdir -p /app/data

EXPOSE 5000

# Flask's development server. docker-compose.prod.yml overrides this with
# gunicorn for anything that isn't a local demo.
CMD ["python", "app.py"]
