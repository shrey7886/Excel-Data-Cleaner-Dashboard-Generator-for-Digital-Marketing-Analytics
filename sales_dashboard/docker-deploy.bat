@echo off
setlocal enabledelayedexpansion

REM Docker Deployment Script for Targetorate (Windows)
REM Usage: docker-deploy.bat [command] [environment]

set PROJECT_NAME=targetorate
set COMPOSE_FILE=docker-compose.yml

REM Colors for output (Windows compatible)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Functions
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:check_docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit /b 1
)
goto :eof

:check_env_file
if not exist .env (
    call :log_warning ".env file not found. Creating from env.example..."
    if exist env.example (
        copy env.example .env >nul
        call :log_info "Please edit .env file with your production settings"
    ) else (
        call :log_error "env.example not found. Please create .env file manually."
        exit /b 1
    )
)
goto :eof

:create_directories
call :log_info "Creating necessary directories..."
if not exist logs mkdir logs
if not exist staticfiles mkdir staticfiles
if not exist media mkdir media
if not exist ssl mkdir ssl
goto :eof

:build_images
call :log_info "Building Docker images..."
docker-compose build --no-cache
goto :eof

:start_services
call :log_info "Starting services..."
docker-compose up -d

REM Wait for services to be ready
call :log_info "Waiting for services to be ready..."
timeout /t 30 /nobreak >nul
goto :eof

:stop_services
call :log_info "Stopping services..."
docker-compose down
goto :eof

:restart_services
call :log_info "Restarting services..."
docker-compose restart
goto :eof

:setup_database
call :log_info "Setting up database..."

REM Wait for database to be ready
call :log_info "Waiting for database to be ready..."
timeout /t 10 /nobreak >nul

REM Run migrations
call :log_info "Running database migrations..."
docker-compose exec -T web python manage.py migrate

REM Create superuser if it doesn't exist
call :log_info "Creating superuser..."
docker-compose exec -T web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.get_or_create(username='admin', defaults={'is_superuser': True, 'is_staff': True, 'email': 'admin@targetorate.com'})[0].set_password('admin123') if not User.objects.filter(username='admin').exists() else None"

REM Create sample data
REM call :log_info "Creating sample data..."
REM docker-compose exec -T web python manage.py create_sample_auth_data 2>nul || call :log_warning "Sample data creation failed (this is normal for first run)"
goto :eof

:collect_static
call :log_info "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput
goto :eof

:check_health
call :log_info "Checking application health..."

REM Wait a bit for services to start
timeout /t 10 /nobreak >nul

REM Check if web service is responding
curl -f http://localhost:8000/health/ >nul 2>&1
if errorlevel 1 (
    call :log_error "Application health check failed"
    exit /b 1
) else (
    call :log_success "Application is healthy!"
)
goto :eof

:show_status
call :log_info "Service status:"
docker-compose ps

call :log_info "Resource usage:"
docker stats --no-stream
goto :eof

:show_logs
set service=%~1
if "%service%"=="" set service=web
call :log_info "Showing logs for %service% service:"
docker-compose logs -f %service%
goto :eof

:backup_database
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
set "backup_file=backup_%timestamp%.sql"

call :log_info "Creating database backup: %backup_file%"
docker-compose exec -T db pg_dump -U postgres sales_dashboard > "%backup_file%"

if errorlevel 1 (
    call :log_error "Backup failed"
    exit /b 1
) else (
    call :log_success "Backup created successfully: %backup_file%"
)
goto :eof

:restore_database
set backup_file=%~1

if "%backup_file%"=="" (
    call :log_error "Please specify backup file"
    echo Usage: %0 restore ^<backup_file^>
    exit /b 1
)

if not exist "%backup_file%" (
    call :log_error "Backup file not found: %backup_file%"
    exit /b 1
)

call :log_info "Restoring database from: %backup_file%"
docker-compose exec -T db psql -U postgres sales_dashboard < "%backup_file%"

if errorlevel 1 (
    call :log_error "Database restore failed"
    exit /b 1
) else (
    call :log_success "Database restored successfully"
)
goto :eof

:update_application
call :log_info "Updating application..."

REM Stop services
call :stop_services

REM Pull latest changes
call :log_info "Pulling latest changes..."
git pull origin main

REM Rebuild images
call :build_images

REM Start services
call :start_services

REM Setup database
call :setup_database

REM Collect static files
call :collect_static

REM Check health
call :check_health
goto :eof

:cleanup
call :log_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
set /p response=
if /i "%response%"=="y" (
    call :log_info "Cleaning up..."
    docker-compose down -v --rmi all
    docker system prune -f
    call :log_success "Cleanup completed"
) else (
    call :log_info "Cleanup cancelled"
)
goto :eof

:show_help
echo Docker Deployment Script for Targetorate
echo.
echo Usage: %0 [command] [options]
echo.
echo Commands:
echo   deploy [env]     Deploy the application (dev/prod)
echo   start            Start all services
echo   stop             Stop all services
echo   restart          Restart all services
echo   status           Show service status
echo   logs [service]   Show logs for a service (default: web)
echo   backup           Create database backup
echo   restore ^<file^>   Restore database from backup
echo   update           Update application from git
echo   cleanup          Remove all containers and images
echo   health           Check application health
echo   help             Show this help message
echo.
echo Examples:
echo   %0 deploy prod
echo   %0 logs web
echo   %0 backup
echo   %0 restore backup_20240101_120000.sql
goto :eof

REM Main script
set command=%~1
if "%command%"=="" set command=help

if "%command%"=="deploy" (
    set environment=%~2
    if "%environment%"=="" set environment=prod
    call :log_info "Deploying Targetorate in %environment% mode..."
    
    call :check_docker
    call :check_env_file
    call :create_directories
    call :build_images
    call :start_services
    call :setup_database
    call :collect_static
    call :check_health
    
    call :log_success "Deployment completed successfully!"
    echo.
    echo 🌐 Application URLs:
    echo    - Main site: http://localhost:8000
    echo    - Admin panel: http://localhost:8000/admin/
    echo    - Health check: http://localhost:8000/health/
    echo.
    echo 👤 Admin credentials:
    echo    - Username: admin
    echo    - Password: admin123
    echo.
    echo 📝 Management commands:
    echo    - View logs: %0 logs
    echo    - Check status: %0 status
    echo    - Stop services: %0 stop
    goto :end
)

if "%command%"=="start" (
    call :check_docker
    call :start_services
    call :log_success "Services started successfully!"
    goto :end
)

if "%command%"=="stop" (
    call :check_docker
    call :stop_services
    call :log_success "Services stopped successfully!"
    goto :end
)

if "%command%"=="restart" (
    call :check_docker
    call :restart_services
    call :log_success "Services restarted successfully!"
    goto :end
)

if "%command%"=="status" (
    call :check_docker
    call :show_status
    goto :end
)

if "%command%"=="logs" (
    call :check_docker
    call :show_logs %~2
    goto :end
)

if "%command%"=="backup" (
    call :check_docker
    call :backup_database
    goto :end
)

if "%command%"=="restore" (
    call :check_docker
    call :restore_database %~2
    goto :end
)

if "%command%"=="update" (
    call :check_docker
    call :update_application
    call :log_success "Application updated successfully!"
    goto :end
)

if "%command%"=="cleanup" (
    call :check_docker
    call :cleanup
    goto :end
)

if "%command%"=="health" (
    call :check_docker
    call :check_health
    goto :end
)

if "%command%"=="help" (
    call :show_help
    goto :end
)

call :show_help

:end 