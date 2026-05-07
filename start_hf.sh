#!/bin/bash

# Start the FastAPI backend in the background
echo "Starting Backend..."
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 5

# Start the Streamlit frontend in the foreground
echo "Starting Frontend..."
cd /app/frontend
export BACKEND_URL=http://localhost:8000
# Hugging Face expects the app to be on port 7860
streamlit run app.py --server.port 7860 --server.address 0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
