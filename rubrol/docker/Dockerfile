# Rubrol Production Dockerfile
# Sub-10ms dynamic PDF/A compilation engine powered by Apache 2.0 Typst
# Turnkey EU Factur-X / ZUGFeRD 2.2 Suite
FROM python:3.12-slim

# OCI Standard Image Metadata & Search Engine Indexing
LABEL org.opencontainers.image.title="Rubrol" \
      org.opencontainers.image.description="High-performance Typst document engine & turnkey EU Factur-X / ZUGFeRD 2.2 sidecar. Sub-15ms compilation, zero Chromium." \
      org.opencontainers.image.url="https://rubrol.com" \
      org.opencontainers.image.documentation="https://rubrol.com/articles/stripe-facturx-zugferd" \
      org.opencontainers.image.source="https://github.com/maxcomperatore/rubrol" \
      org.opencontainers.image.vendor="Rubrol" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.keywords="factur-x,zugferd,en16931,typst,e-invoice,e-invoicing,pdfa3,pdf-generator,gotenberg-alternative,puppeteer-alternative"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir typst pypdf

# Copy application files
COPY rubrol /app/rubrol
COPY rubrol.py /app/rubrol.py

# Default environment configuration
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run Rubrol Production Sidecar
CMD ["python", "rubrol.py", "serve", "--host", "0.0.0.0", "--port", "8080"]
