#!/bin/bash

set -e

# Emergency Rollback Script for Django Cookiecutter
# Based on community best practices

echo "🚨 Starting emergency rollback..."

# 1. Stop all services
echo "⏹️  Stopping all services..."
docker-compose -f docker-compose.production.yml down

# 2. Restore database from backup (if available)
if [ -n "${BACKUP_FILE:-}" ]; then
    echo "🗄️  Restoring database from backup: ${BACKUP_FILE}"
    docker-compose -f docker-compose.production.yml run --rm awscli restore "${BACKUP_FILE}"
else
    echo "⚠️  No backup file specified. Database will remain as is."
fi

# 3. Start previous version (you should tag your images)
echo "🔄 Starting previous version..."
# docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

echo "✅ Rollback completed!"
echo "📊 Check application status: docker-compose -f docker-compose.production.yml logs -f"
