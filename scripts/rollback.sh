#!/bin/bash

# Production Rollback Script
# This script rolls back to the previous version in case of deployment failure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔄 Starting production rollback..."

# Check if backup file exists
if [ ! -f "docker-compose.production.yml.backup" ]; then
    print_error "No backup file found: docker-compose.production.yml.backup"
    print_error "Cannot perform rollback. Manual intervention required."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running"
    exit 1
fi

# Confirm rollback
echo ""
print_warning "⚠️  WARNING: This will rollback to the previous version!"
print_warning "All current changes will be lost!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    print_status "Rollback cancelled by user"
    exit 0
fi

# Stop all current services
print_status "Stopping current services..."
docker compose -f docker-compose.production.yml down --timeout 30

# Restore previous configuration
print_status "Restoring previous configuration..."
mv docker-compose.production.yml.backup docker-compose.production.yml

# Start services with previous configuration
print_status "Starting services with previous configuration..."
if docker compose -f docker-compose.production.yml up -d; then
    print_success "Services started with previous configuration"
else
    print_error "Failed to start services with previous configuration"
    print_error "Manual intervention required!"
    exit 1
fi

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 15

# Verify services are running
print_status "Verifying services are running..."
if docker compose -f docker-compose.production.yml ps | grep -q "Up"; then
    print_success "Rollback completed successfully!"
    echo ""
    print_status "Current service status:"
    docker compose -f docker-compose.production.yml ps
    echo ""
    print_status "Rollback completed at: $(date)"
    print_status "Previous version is now running"
else
    print_error "Services are not running properly after rollback"
    print_error "Manual intervention required!"
    exit 1
fi

echo ""
print_warning "💡 Remember to investigate why the deployment failed"
print_warning "💡 Check logs: docker compose -f docker-compose.production.yml logs -f"
print_warning "💡 Check status: ./scripts/status.sh"
