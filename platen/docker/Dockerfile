# Platen Production Dockerfile
# Lightweight, high-throughput PDF/A Sidecar powered by Apache 2.0 Typst
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir typst pypdf

# Copy application files
COPY platen /app/platen

# Default environment configuration
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run Platen Production Sidecar
CMD ["python", "platen/core/server.py", "--host", "0.0.0.0", "--port", "8080"]
