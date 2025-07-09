# Sales Dashboard - Production Deployment Guide

This guide covers deploying the Sales Dashboard application to production using various methods.

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- Domain name (optional, for SSL)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd sales_dashboard
cp env.example .env
# Edit .env with your production settings
```

### 2. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 3. Initial Setup
```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data
docker-compose exec web python manage.py load_demo_data
```

## 🖥️ Manual Deployment (Ubuntu/Debian)

### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Nginx

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git curl
```

### 2. Application Setup
```bash
# Clone repository
git clone <repository-url>
cd sales_dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env
# Edit .env with your settings
```

### 3. Database Setup
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE sales_dashboard;
CREATE USER sales_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sales_dashboard TO sales_user;
\q

# Run migrations
python manage.py migrate
```

### 4. Static Files and Media
```bash
# Collect static files
python manage.py collectstatic --noinput

# Create media directory
mkdir -p media
```

### 5. Gunicorn Setup
```bash
# Test Gunicorn
gunicorn --config gunicorn.conf.py sales_dashboard.wsgi:application

# Create systemd service
sudo cp deploy.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/deploy.sh
sudo ./deploy.sh
```

### 6. Nginx Configuration
```bash
# Copy Nginx config
sudo cp nginx.conf /etc/nginx/sites-available/sales_dashboard
sudo ln -s /etc/nginx/sites-available/sales_dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=sales_dashboard
DB_USER=sales_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### Application Logs
```bash
# View application logs
sudo journalctl -u sales_dashboard -f

# View Celery logs
sudo journalctl -u sales_dashboard_celery -f
sudo journalctl -u sales_dashboard_celerybeat -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Checks
```bash
# Application health
curl http://yourdomain.com/health/

# Database connection
python manage.py dbshell

# Redis connection
redis-cli ping
```

## 🔄 Maintenance

### Regular Tasks
```bash
# Update application
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sales_dashboard

# Backup database
pg_dump sales_dashboard > backup_$(date +%Y%m%d).sql

# Clean old logs
sudo journalctl --vacuum-time=30d
```

### Performance Optimization
```bash
# Database optimization
python manage.py dbshell
VACUUM ANALYZE;

# Cache warming
python manage.py shell
from django.core.cache import cache
cache.clear()
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check logs
sudo journalctl -u sales_dashboard -n 50

# Check permissions
sudo chown -R $USER:www-data /path/to/app
sudo chmod -R 755 /path/to/app
```

#### 2. Database Connection Issues
```bash
# Test connection
python manage.py dbshell

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### 3. Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check Nginx configuration
sudo nginx -t
```

#### 4. Celery Tasks Not Running
```bash
# Check Celery status
sudo systemctl status sales_dashboard_celery

# Test Celery
celery -A sales_dashboard inspect active
```

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Configure firewall (UFW)
- [ ] Enable SSL/TLS
- [ ] Set up regular backups
- [ ] Configure rate limiting
- [ ] Enable security headers
- [ ] Set up monitoring
- [ ] Regular security updates

## 📈 Scaling

### Horizontal Scaling
```bash
# Multiple Gunicorn workers
# Edit gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1

# Load balancer setup
# Use Nginx upstream with multiple application servers
```

### Database Scaling
```bash
# Read replicas
# Configure Django for read/write splitting
# Use connection pooling
```

### Caching
```bash
# Redis clustering
# CDN for static files
# Application-level caching
```

## 📞 Support

For deployment issues:
1. Check the logs: `sudo journalctl -u sales_dashboard -f`
2. Verify configuration files
3. Test individual components
4. Check system resources: `htop`, `df -h`, `free -h`

## 🔄 Updates

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Restart services
sudo systemctl restart sales_dashboard
sudo systemctl restart sales_dashboard_celery
```

### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart services if needed
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis
``` 