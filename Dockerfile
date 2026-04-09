FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY app.py .
COPY preprocess_data.py .
COPY retrain_v2.py .
COPY train_model.py .
COPY recruitment_model.pth .
COPY verified_templates.json .
COPY ui_templates.json .
COPY index.html .

# Copy any remaining utility scripts
COPY *.py .

EXPOSE 5000

CMD ["python", "app.py"]
