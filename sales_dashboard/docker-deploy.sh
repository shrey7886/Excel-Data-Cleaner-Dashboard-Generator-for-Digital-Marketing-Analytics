#!/bin/bash

# Docker Deployment Script for Targetorate
# Usage: ./docker-deploy.sh [command] [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="targetorate"
COMPOSE_FILE="docker-compose.yml"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

check_env_file() {
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from env.example..."
        if [ -f env.example ]; then
            cp env.example .env
            log_info "Please edit .env file with your production settings"
        else
            log_error "env.example not found. Please create .env file manually."
            exit 1
        fi
    fi
}

create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p logs
    mkdir -p staticfiles
    mkdir -p media
    mkdir -p ssl
}

build_images() {
    log_info "Building Docker images..."
    docker-compose build --no-cache
}

start_services() {
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
}

stop_services() {
    log_info "Stopping services..."
    docker-compose down
}

restart_services() {
    log_info "Restarting services..."
    docker-compose restart
}

setup_database() {
    log_info "Setting up database..."
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    log_info "Running database migrations..."
    docker-compose exec -T web python manage.py migrate
    
    # Create superuser if it doesn't exist
    log_info "Creating superuser..."
    docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@targetorate.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    
    # Create sample data
    log_info "Creating sample data..."
    docker-compose exec -T web python manage.py create_sample_auth_data || log_warning "Sample data creation failed (this is normal for first run)"
}

collect_static() {
    log_info "Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
}

check_health() {
    log_info "Checking application health..."
    
    # Wait a bit for services to start
    sleep 10
    
    # Check if web service is responding
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        log_success "Application is healthy!"
    else
        log_error "Application health check failed"
        return 1
    fi
}

show_status() {
    log_info "Service status:"
    docker-compose ps
    
    log_info "Resource usage:"
    docker stats --no-stream
}

show_logs() {
    local service=${1:-web}
    log_info "Showing logs for $service service:"
    docker-compose logs -f $service
}

backup_database() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backup_${timestamp}.sql"
    
    log_info "Creating database backup: $backup_file"
    docker-compose exec -T db pg_dump -U postgres sales_dashboard > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "Backup created successfully: $backup_file"
    else
        log_error "Backup failed"
        return 1
    fi
}

restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Please specify backup file"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_info "Restoring database from: $backup_file"
    docker-compose exec -T db psql -U postgres sales_dashboard < "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "Database restored successfully"
    else
        log_error "Database restore failed"
        return 1
    fi
}

update_application() {
    log_info "Updating application..."
    
    # Stop services
    stop_services
    
    # Pull latest changes
    log_info "Pulling latest changes..."
    git pull origin main
    
    # Rebuild images
    build_images
    
    # Start services
    start_services
    
    # Setup database
    setup_database
    
    # Collect static files
    collect_static
    
    # Check health
    check_health
}

cleanup() {
    log_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

show_help() {
    echo "Docker Deployment Script for Targetorate"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  deploy [env]     Deploy the application (dev/prod)"
    echo "  start            Start all services"
    echo "  stop             Stop all services"
    echo "  restart          Restart all services"
    echo "  status           Show service status"
    echo "  logs [service]   Show logs for a service (default: web)"
    echo "  backup           Create database backup"
    echo "  restore <file>   Restore database from backup"
    echo "  update           Update application from git"
    echo "  cleanup          Remove all containers and images"
    echo "  health           Check application health"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy prod"
    echo "  $0 logs web"
    echo "  $0 backup"
    echo "  $0 restore backup_20240101_120000.sql"
}

# Main script
case "${1:-help}" in
    "deploy")
        environment=${2:-prod}
        log_info "Deploying Targetorate in $environment mode..."
        
        check_docker
        check_env_file
        create_directories
        build_images
        start_services
        setup_database
        collect_static
        check_health
        
        log_success "Deployment completed successfully!"
        echo ""
        echo "🌐 Application URLs:"
        echo "   - Main site: http://localhost:8000"
        echo "   - Admin panel: http://localhost:8000/admin/"
        echo "   - Health check: http://localhost:8000/health/"
        echo ""
        echo "👤 Admin credentials:"
        echo "   - Username: admin"
        echo "   - Password: admin123"
        echo ""
        echo "📝 Management commands:"
        echo "   - View logs: $0 logs"
        echo "   - Check status: $0 status"
        echo "   - Stop services: $0 stop"
        ;;
    
    "start")
        check_docker
        start_services
        log_success "Services started successfully!"
        ;;
    
    "stop")
        check_docker
        stop_services
        log_success "Services stopped successfully!"
        ;;
    
    "restart")
        check_docker
        restart_services
        log_success "Services restarted successfully!"
        ;;
    
    "status")
        check_docker
        show_status
        ;;
    
    "logs")
        check_docker
        show_logs $2
        ;;
    
    "backup")
        check_docker
        backup_database
        ;;
    
    "restore")
        check_docker
        restore_database $2
        ;;
    
    "update")
        check_docker
        update_application
        log_success "Application updated successfully!"
        ;;
    
    "cleanup")
        check_docker
        cleanup
        ;;
    
    "health")
        check_docker
        check_health
        ;;
    
    "help"|*)
        show_help
        ;;
esac 