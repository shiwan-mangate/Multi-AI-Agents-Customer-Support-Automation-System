# =============================================================================
# Multi-Agent Customer Support Platform
# Production Dockerfile
# =============================================================================

# -----------------------------------------------------------------------------
# Base Image
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# -----------------------------------------------------------------------------
# Python Configuration
# -----------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# HuggingFace / Transformers Cache
ENV HF_HOME=/models/huggingface
ENV TRANSFORMERS_CACHE=/models/huggingface
ENV HF_HUB_CACHE=/models/huggingface

# -----------------------------------------------------------------------------
# System Dependencies
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    ca-certificates \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Working Directory
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# Install Python Dependencies
# -----------------------------------------------------------------------------
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -v -r requirements.txt

# -----------------------------------------------------------------------------
# Copy Application Source
# -----------------------------------------------------------------------------
COPY . .

# -----------------------------------------------------------------------------
# Create Persistent Model Cache
# -----------------------------------------------------------------------------
RUN mkdir -p /models/huggingface

# -----------------------------------------------------------------------------
# Expose FastAPI Port
# -----------------------------------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------------------------------
# Default Command
# -----------------------------------------------------------------------------
# Used by API container.
# Worker containers override this in docker-compose.yml.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]