#!/bin/bash

# Production Service Status Script
# This script checks the status of all services in production

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

echo "🔍 Checking production service status..."

# Check if docker-compose file exists
if [ ! -f "docker-compose.production.yml" ]; then
    print_error "docker-compose.production.yml not found"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running"
    exit 1
fi

# Display overall status
print_status "Overall service status:"
docker compose -f docker-compose.production.yml ps

echo ""

# Check each service individually
services=("postgres" "redis" "django" "traefik" "celeryworker" "celerybeat" "flower")

for service in "${services[@]}"; do
    print_status "Checking $service..."
    
    # Get service status
    status=$(docker compose -f docker-compose.production.yml ps $service --format json | jq -r '.[0].State' 2>/dev/null || echo "unknown")
    
    case $status in
        "running")
            print_success "$service is running"
            
            # Additional checks for specific services
            case $service in
                "postgres")
                    if docker compose -f docker-compose.production.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
                        print_success "  - PostgreSQL is accepting connections"
                    else
                        print_warning "  - PostgreSQL is not accepting connections"
                    fi
                    ;;
                "django")
                    # Check if Django is responding
                    if docker compose -f docker-compose.production.yml exec -T django python manage.py check > /dev/null 2>&1; then
                        print_success "  - Django is responding to commands"
                    else
                        print_warning "  - Django is not responding to commands"
                    fi
                    ;;
                "redis")
                    # Check if Redis is responding
                    if docker compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
                        print_success "  - Redis is responding to ping"
                    else
                        print_warning "  - Redis is not responding to ping"
                    fi
                    ;;
            esac
            ;;
        "exited")
            print_error "$service has exited"
            ;;
        "restarting")
            print_warning "$service is restarting"
            ;;
        "paused")
            print_warning "$service is paused"
            ;;
        "unknown"|"")
            print_error "$service status unknown or not found"
            ;;
        *)
            print_warning "$service status: $status"
            ;;
    esac
    
    echo ""
done

# Check resource usage
print_status "Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""

# Check logs for errors (last 10 lines)
print_status "Recent error logs (last 10 lines):"
for service in "${services[@]}"; do
    if docker compose -f docker-compose.production.yml ps $service | grep -q "Up"; then
        print_status "Checking $service logs for errors..."
        docker compose -f docker-compose.production.yml logs --tail=10 $service | grep -i "error\|exception\|traceback" || echo "  No errors found"
        echo ""
    fi
done

# Check disk space
print_status "Disk space usage:"
df -h | grep -E "(Filesystem|/dev/)"

echo ""

# Check Docker disk usage
print_status "Docker disk usage:"
docker system df

echo ""

print_status "Status check completed!"
echo "💡 Use 'docker compose -f docker-compose.production.yml logs -f [service]' to follow logs"
echo "💡 Use 'docker compose -f docker-compose.production.yml restart [service]' to restart a service"
