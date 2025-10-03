# Dockerfile dla SPA Automation (zgodnie z b24pysdk pattern)
# Bazuje na oficjalnym podejściu: https://github.com/bitrix24/b24pysdk

FROM python:3.12-slim

# Metadata
LABEL maintainer="ralengroup"
LABEL description="SPA Automation with b24pysdk"

# Ustaw working directory
WORKDIR /app

# Zainstaluj system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements
COPY requirements.txt .

# Zainstaluj Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Ustaw Python path
ENV PYTHONPATH=/app

# Expose port (Render uses port 10000)
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:10000/health || exit 1

# Run the webhook application
CMD ["python", "src/webhook.py"]


