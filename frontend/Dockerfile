FROM python:3.10-slim

RUN groupadd -r tenderguard && useradd -r -g tenderguard tenderguard

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create certs directory (certs will be mounted via docker-compose)
RUN mkdir -p /app/certs

# Set Streamlit configurations
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_SERVER_SSL_CERT_FILE=/app/certs/cert.pem
ENV STREAMLIT_SERVER_SSL_KEY_FILE=/app/certs/key.pem

RUN chown -R tenderguard:tenderguard /app
USER tenderguard

EXPOSE 8501

# Run Streamlit (Flexible for Local SSL or Cloud Deployment)
CMD streamlit run app.py --server.port ${PORT:-8501} ${STREAMLIT_SERVER_SSL_CERT_FILE:+--server.sslCertFile $STREAMLIT_SERVER_SSL_CERT_FILE} ${STREAMLIT_SERVER_SSL_KEY_FILE:+--server.sslKeyFile $STREAMLIT_SERVER_SSL_KEY_FILE}
