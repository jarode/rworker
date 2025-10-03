#!/bin/bash
# Skrypt uruchamiający production webhook

set -e  # Exit on error

echo "=========================================="
echo "🚀 SPA Automation - Production Deployment"
echo "=========================================="

# Sprawdź czy .env istnieje
if [ ! -f .env ]; then
    echo "❌ BŁĄD: Brak pliku .env"
    echo "Skopiuj .env.example i uzupełnij credentials"
    exit 1
fi

# Sprawdź czy Docker działa
if ! docker ps > /dev/null 2>&1; then
    echo "❌ BŁĄD: Docker nie działa"
    echo "Uruchom Docker Desktop"
    exit 1
fi

echo ""
echo "✅ Docker działa"
echo "✅ Plik .env istnieje"
echo ""

# Build image
echo "🔨 Budowanie Docker image..."
docker compose -f docker-compose.prod.yml build

echo ""
echo "✅ Image zbudowany"
echo ""

# Uruchom webhook
echo "🚀 Uruchamianie webhook..."
docker compose -f docker-compose.prod.yml up -d spa-webhook

echo ""
echo "⏳ Czekam 5s na start..."
sleep 5

# Health check
echo ""
echo "🏥 Health check..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Webhook działa!"
    echo ""
    echo "📊 Dostępne endpointy:"
    echo "  http://localhost:5000/health"
    echo "  http://localhost:5000/webhook/spa/<spa_id>"
    echo "  http://localhost:5000/webhook/spa/<spa_id>/dry-run"
    echo ""
    echo "📝 Logi:"
    echo "  docker compose -f docker-compose.prod.yml logs -f spa-webhook"
    echo ""
    echo "🛑 Zatrzymanie:"
    echo "  docker compose -f docker-compose.prod.yml down"
else
    echo "❌ Health check failed!"
    echo "Sprawdź logi:"
    echo "  docker compose -f docker-compose.prod.yml logs spa-webhook"
    exit 1
fi

echo "=========================================="
echo "✅ DEPLOYMENT ZAKOŃCZONY SUKCESEM!"
echo "=========================================="

