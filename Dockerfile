# syntax=docker/dockerfile:1
FROM python:3.12-slim

# System deps for PyMuPDF and pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway injects PORT env var; default to 8080 for local runs
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
