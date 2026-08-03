FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend modules (app, db, auth, models, training + utility scripts)
COPY *.py .

# Model weights and UI template data
COPY recruitment_model.pth .
COPY verified_templates.json .
COPY ui_templates.json .

# Holds the SQLite file; mount a volume here so accounts survive a rebuild
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "app.py"]
