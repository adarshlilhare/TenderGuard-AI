FROM python:3.10-slim

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all requirements and install
COPY backend/requirements.txt ./backend_reqs.txt
COPY frontend/requirements.txt ./frontend_reqs.txt
RUN pip install --no-cache-dir -r backend_reqs.txt
RUN pip install --no-cache-dir -r frontend_reqs.txt

# Pre-download the HuggingFace model for offline use
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')"

# Copy the entire project
COPY . .

# Set permissions
RUN chmod +x start_hf.sh
RUN mkdir -p /app/data && chmod 777 /app/data

# Hugging Face Spaces run as a low-privilege user (UID 1000)
# We need to ensure they can write to the data directory
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose the port Hugging Face expects
EXPOSE 7860

# Use the startup script
CMD ["./start_hf.sh"]
