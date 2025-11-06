# Streamlit dashboard for Casa Inteligente
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (optional: git for future extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY docker/streamlit/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit application
COPY dashboard.py ./dashboard.py

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false \
    STREAMLIT_METRICS_DISABLE=true

# API base URL must be provided via env when deploying
ENV API_BASE_URL="http://localhost:8000"

# Expose default Streamlit port
EXPOSE 8501

# Entrypoint
CMD ["streamlit", "run", "dashboard.py"]
