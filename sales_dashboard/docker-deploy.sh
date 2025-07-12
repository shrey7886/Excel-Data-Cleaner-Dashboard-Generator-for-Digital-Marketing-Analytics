#!/bin/bash

# Docker Deployment Script for Marketing Analytics Dashboard
# Usage: ./docker-deploy.sh [production|development]

set -e

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Generate secret key
generate_secret_key() {
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Production Environment Variables
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (will be set by Docker Compose)
DATABASE_URL=postgresql://postgres:postgres@db:5432/sales_dashboard

# Redis (will be set by Docker Compose)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Settings (update these)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Keys (optional)
GOOGLE_ADS_API_KEY=your-google-ads-api-key
LINKEDIN_ADS_API_KEY=your-linkedin-ads-api-key
MAILCHIMP_API_KEY=your-mailchimp-api-key
ZOHO_API_KEY=your-zoho-api-key
DEMANDBASE_API_KEY=your-demandbase-api-key
EOF
        print_success "Created .env file"
    else
        print_warning ".env file already exists"
    fi
}

# Build and start services
deploy() {
    local environment=${1:-production}
    
    print_status "Deploying in $environment mode..."
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput
    
    # Create superuser if needed
    print_status "Do you want to create a superuser? (y/n): "
    read -r create_superuser
    if [[ $create_superuser =~ ^[Yy]$ ]]; then
        docker-compose exec web python manage.py createsuperuser
    fi
    
    print_success "Deployment completed!"
}

# Show status
status() {
    print_status "Checking service status..."
    docker-compose ps
    
    print_status "Recent logs:"
    docker-compose logs --tail=20
}

# Show logs
logs() {
    local service=${1:-web}
    print_status "Showing logs for $service service..."
    docker-compose logs -f "$service"
}

# Stop services
stop() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "Services stopped"
}

# Clean up
cleanup() {
    print_warning "This will remove all containers, volumes, and images. Are you sure? (y/n): "
    read -r confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Cleanup completed"
    fi
}

# Show help
show_help() {
    echo "Docker Deployment Script for Marketing Analytics Dashboard"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy [production|development]  Deploy the application"
    echo "  status                          Show service status"
    echo "  logs [service]                  Show logs (default: web)"
    echo "  stop                            Stop all services"
    echo "  cleanup                         Remove all containers and volumes"
    echo "  help                            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy production"
    echo "  $0 logs web"
    echo "  $0 status"
}

# Main script
main() {
    case "${1:-help}" in
        deploy)
            check_docker
            generate_secret_key
            deploy "$2"
            ;;
        status)
            status
            ;;
        logs)
            logs "$2"
            ;;
        stop)
            stop
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 