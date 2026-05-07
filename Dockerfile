# ============================================================
# Vyntrix Intelligence — Full-Stack Docker Image
# Backend: FastAPI + PyTorch (port 8000)
# Frontend: Nginx serving static files (port 3000)
# ============================================================

FROM python:3.11-slim AS base

# Prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Backend Setup ----
WORKDIR /app/backend

# Copy requirements first for Docker layer caching
COPY backend/requirements.txt .

# Install Python dependencies (CPU-only PyTorch to keep image smaller)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.2.1+cpu torchvision==0.17.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/main.py .
COPY backend/model.py .
COPY backend/database.py .
COPY backend/models_db.py .
COPY backend/auth.py .
COPY backend/webhooks.py .
COPY backend/self_healing.py .

# ---- Frontend Setup ----
WORKDIR /app/frontend

# Copy all frontend static files
COPY index.html .
COPY solutions.html .
COPY lab.html .
COPY contact.html .
COPY style.css .
COPY script.js .
COPY assets/ ./assets/

# ---- Nginx Config ----
RUN rm -f /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/conf.d/vyntrix.conf

# ---- Supervisor Config (runs both nginx + uvicorn) ----
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Start supervisor (manages both nginx and uvicorn)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
