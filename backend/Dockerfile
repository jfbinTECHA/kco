# ==========================================================
# 🧠 Kilocode Standalone Backend Dockerfile
# ==========================================================
# Builds FastAPI + Kilocode bridge environment for local/demo
# ==========================================================

FROM python:3.12-slim

WORKDIR /app

# Copy requirements into container and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source code
COPY app /app/app

# Expose backend API port
EXPOSE 8001

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]