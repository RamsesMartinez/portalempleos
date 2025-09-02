#!/bin/bash

set -e

# Production Deployment Script for Django Cookiecutter
# Based on community best practices

echo "🚀 Starting production deployment..."

# 1. Build and push Docker images
echo "📦 Building Docker images..."
docker compose -f docker-compose.production.yml build

# 2. Deploy infrastructure first (PostgreSQL, Redis)
echo "🗄️  Starting infrastructure services..."
docker compose -f docker-compose.production.yml up -d postgres redis

# 3. Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# 4. Run migrations (separate from application startup)
echo "🔄 Running database migrations..."
docker compose -f docker-compose.production.yml run --rm django /app/compose/production/django/migrate

# 5. Start application services
echo "🌐 Starting application services..."
docker compose -f docker-compose.production.yml up -d django traefik

# 6. Start background workers
echo "⚙️  Starting background workers..."
docker compose -f docker-compose.production.yml up -d celeryworker celerybeat flower

echo "✅ Deployment completed successfully!"
echo "🌍 Your application is now running at: https://portalempleos.com.mx"
echo "📊 Monitor with: docker compose -f docker-compose.production.yml logs -f"
