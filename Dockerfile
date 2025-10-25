# Maple Mover - Fixed Production Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# System deps
RUN apt-get update && apt-get install -y \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install deps
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy project source
COPY src/ ./src/
COPY maple_mover.env ./maple_mover.env

# Optional: Streamlit config directory
COPY .streamlit/ .streamlit/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port (use Docker ARG for flexibility)
ARG PORT=8501
ENV STREAMLIT_SERVER_PORT=$PORT
EXPOSE $PORT

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Run the app
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
