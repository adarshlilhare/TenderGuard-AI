FROM python:3.10-slim

# Install system dependencies for OCR (Tesseract and Poppler for pdf2image)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r tenderguard && useradd -r -g tenderguard tenderguard

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace model so it's cached in the Docker image
# This ensures true offline capability when the container runs
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')"

# Create data and certs directories and set permissions
RUN mkdir -p /app/data /app/certs && chown -R tenderguard:tenderguard /app

# Copy application code
COPY . .
RUN chown -R tenderguard:tenderguard /app

# Switch to non-root user
USER tenderguard

# Expose port
EXPOSE 8000

# Run FastAPI app (Flexible for Local SSL or Cloud Deployment)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} ${SSL_KEYFILE:+--ssl-keyfile $SSL_KEYFILE} ${SSL_CERTFILE:+--ssl-certfile $SSL_CERTFILE}
