#!/bin/bash

set -e

# Production Deployment Script for Django Cookiecutter
# Based on community best practices

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if service is running
check_service() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1
    
    print_status "Checking if $service is running..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose -f docker-compose.production.yml ps $service | grep -q "Up"; then
            print_success "$service is running"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "$service failed to start after $max_attempts attempts"
            return 1
        fi
        
        print_status "Waiting for $service to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Function to wait for database to be ready
wait_for_database() {
    print_status "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose -f docker-compose.production.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "PostgreSQL failed to become ready after $max_attempts attempts"
            return 1
        fi
        
        print_status "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Function to check if migrations are needed
check_migrations() {
    print_status "Checking if migrations are needed..."
    
    if docker compose -f docker-compose.production.yml run --rm django python manage.py showmigrations --list | grep -q "\[ \]"; then
        print_warning "Pending migrations detected"
        return 0
    else
        print_success "No pending migrations"
        return 1
    fi
}

# Function to backup database before deployment
backup_database() {
    print_status "Creating database backup before deployment..."
    
    if docker compose -f docker-compose.production.yml run --rm awscli /backup; then
        print_success "Database backup completed"
    else
        print_warning "Database backup failed, continuing with deployment..."
    fi
}

# Function to rollback on failure
rollback() {
    print_error "Deployment failed, rolling back..."
    
    # Stop all services
    docker compose -f docker-compose.production.yml down
    
    # Restart previous version if available
    if [ -f "docker-compose.production.yml.backup" ]; then
        print_status "Restoring previous configuration..."
        mv docker-compose.production.yml.backup docker-compose.production.yml
        docker compose -f docker-compose.production.yml up -d
    fi
    
    print_error "Rollback completed. Check logs for details."
    exit 1
}

# Set trap for rollback on error
trap rollback ERR

echo "🚀 Starting production deployment..."

# 0. Pre-deployment checks
print_status "Performing pre-deployment checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker compose > /dev/null 2>&1; then
    print_error "docker compose is not available"
    exit 1
fi

# Check if .env files exist
if [ ! -f ".envs/.production/.django" ]; then
    print_error "Production environment file not found: .envs/.production/.django"
    exit 1
fi

print_success "Pre-deployment checks passed"

# 1. Backup current configuration and database
print_status "Creating backup of current configuration..."
cp docker-compose.production.yml docker-compose.production.yml.backup

backup_database

# 2. Build and push Docker images
print_status "Building Docker images..."
if docker compose -f docker-compose.production.yml build; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# 3. Stop existing services gracefully
print_status "Stopping existing services..."
docker compose -f docker-compose.production.yml down --timeout 30

# 4. Deploy infrastructure first (PostgreSQL, Redis)
print_status "Starting infrastructure services..."
if docker compose -f docker-compose.production.yml up -d postgres redis; then
    print_success "Infrastructure services started"
else
    print_error "Failed to start infrastructure services"
    exit 1
fi

# 5. Wait for database to be ready
if ! wait_for_database; then
    print_error "Database failed to become ready"
    exit 1
fi

# 6. Run migrations (separate from application startup)
print_status "Running database migrations..."
if docker compose -f docker-compose.production.yml run --rm django /app/compose/production/django/migrate; then
    print_success "Database migrations completed"
else
    print_error "Database migrations failed"
    exit 1
fi

# 7. Start application services
print_status "Starting application services..."
if docker compose -f docker-compose.production.yml up -d django traefik; then
    print_success "Application services started"
else
    print_error "Failed to start application services"
    exit 1
fi

# 8. Wait for Django to be ready
print_status "Waiting for Django to be ready..."
sleep 10

# Check if Django is responding
if ! check_service "django" 30; then
    print_error "Django service failed to start properly"
    exit 1
fi

# 9. Start background workers
print_status "Starting background workers..."
if docker compose -f docker-compose.production.yml up -d celeryworker celerybeat flower; then
    print_success "Background workers started"
else
    print_error "Failed to start background workers"
    exit 1
fi

# 10. Verify all services are running
print_status "Verifying all services are running..."

services=("postgres" "redis" "django" "traefik" "celeryworker" "celerybeat" "flower")
all_running=true

for service in "${services[@]}"; do
    if ! check_service "$service" 10; then
        print_error "$service is not running"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    print_error "Not all services are running properly"
    exit 1
fi

# 11. Post-deployment verification
print_status "Performing post-deployment verification..."

# Check if Django is responding to HTTP requests
print_status "Testing Django application..."
if docker compose -f docker-compose.production.yml exec -T django python manage.py check --deploy; then
    print_success "Django deployment check passed"
else
    print_warning "Django deployment check had warnings"
fi

# Clean up backup file
rm -f docker-compose.production.yml.backup

print_success "Deployment completed successfully!"
echo "🌍 Your application is now running at: https://portalempleos.com.mx"
echo "📊 Monitor with: docker compose -f docker-compose.production.yml logs -f"
echo "🔍 Check service status with: docker compose -f docker-compose.production.yml ps"

# Display service status
print_status "Current service status:"
docker compose -f docker-compose.production.yml ps
