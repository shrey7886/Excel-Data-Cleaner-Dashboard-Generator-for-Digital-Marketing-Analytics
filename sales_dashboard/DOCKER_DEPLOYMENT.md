# 🐳 Docker Deployment Guide

## Quick Start

### 1. **Prerequisites**
- Docker installed
- Docker Compose installed
- Git (to clone the repository)

### 2. **Deploy with One Command**
```bash
# Make the deployment script executable
chmod +x docker-deploy.sh

# Deploy the application
./docker-deploy.sh deploy production
```

### 3. **Access Your Application**
- **Dashboard**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

## 🚀 Complete Deployment Steps

### Step 1: Clone and Navigate
```bash
git clone <your-repo-url>
cd sales_dashboard
```

### Step 2: Deploy with Docker
```bash
# Deploy all services
./docker-deploy.sh deploy production

# Or manually:
docker-compose up -d
```

### Step 3: Initialize Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## 📊 Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │    │  Django Web     │    │   PostgreSQL    │
│   (Optional)    │◄──►│   (8000)        │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Cache/Queue) │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Celery        │
                       │   (Background)  │
                       └─────────────────┘
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```bash
# Production Environment Variables
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (auto-configured by Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/sales_dashboard

# Redis (auto-configured by Docker)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Settings
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
```

## 🛠️ Management Commands

### View Status
```bash
./docker-deploy.sh status
# or
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
./docker-deploy.sh logs web
./docker-deploy.sh logs db
./docker-deploy.sh logs redis
```

### Stop Services
```bash
./docker-deploy.sh stop
# or
docker-compose down
```

### Clean Up Everything
```bash
./docker-deploy.sh cleanup
# or
docker-compose down -v --rmi all
docker system prune -f
```

## 🌐 Production Deployment

### 1. **Cloud Deployment (AWS, GCP, Azure)**

#### AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t marketing-dashboard .
docker tag marketing-dashboard:latest <account>.dkr.ecr.us-east-1.amazonaws.com/marketing-dashboard:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/marketing-dashboard:latest
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy marketing-dashboard \
  --image gcr.io/<project>/marketing-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 2. **VPS Deployment**

#### DigitalOcean Droplet
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your repository
git clone <your-repo-url>
cd sales_dashboard

# Deploy
./docker-deploy.sh deploy production
```

#### Linode/Akamai
```bash
# Similar to DigitalOcean
# Install Docker and deploy
```

### 3. **Self-Hosted Server**

#### Ubuntu Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER

# Deploy application
./docker-deploy.sh deploy production
```

## 🔒 Security Configuration

### 1. **SSL/HTTPS Setup**

#### Let's Encrypt with Nginx
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Update nginx.conf for HTTPS
```

#### Self-Signed Certificate (Development)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/nginx-selfsigned.key \
  -out nginx/ssl/nginx-selfsigned.crt
```

### 2. **Firewall Configuration**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (CentOS/RHEL)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## 📈 Monitoring & Maintenance

### 1. **Health Checks**
```bash
# Check application health
curl http://localhost:8000/health/

# Check all services
docker-compose ps
```

### 2. **Backup Strategy**
```bash
# Database backup
docker-compose exec db pg_dump -U postgres sales_dashboard > backup.sql

# Media files backup
tar -czf media_backup.tar.gz media/

# Full backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U postgres sales_dashboard > "backup_${DATE}.sql"
tar -czf "media_backup_${DATE}.tar.gz" media/
```

### 3. **Log Rotation**
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/marketing-dashboard

# Add configuration
/path/to/your/app/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill the process
sudo kill -9 <PID>
```

#### 2. **Database Connection Issues**
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### 3. **Static Files Not Loading**
```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx configuration
docker-compose logs nginx
```

#### 4. **Memory Issues**
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Performance Optimization

#### 1. **Database Optimization**
```sql
-- Add indexes
CREATE INDEX idx_client_data_created ON client_data(created_at);
CREATE INDEX idx_ml_predictions_date ON ml_predictions(prediction_date);
```

#### 2. **Caching Configuration**
```python
# settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'TIMEOUT': 300,
    }
}
```

#### 3. **Gunicorn Optimization**
```python
# gunicorn.conf.py
workers = 3
worker_class = 'gevent'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
```

## 🔄 Updates & Maintenance

### 1. **Application Updates**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
```

### 2. **Database Migrations**
```bash
# Create migration
docker-compose exec web python manage.py makemigrations

# Apply migration
docker-compose exec web python manage.py migrate
```

### 3. **Security Updates**
```bash
# Update base images
docker-compose pull

# Rebuild with security updates
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Scaling

### 1. **Horizontal Scaling**
```bash
# Scale web services
docker-compose up -d --scale web=3

# Use load balancer
# Configure nginx as load balancer
```

### 2. **Vertical Scaling**
```bash
# Increase resources in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
```

## 🎯 Production Checklist

- [ ] SSL certificate configured
- [ ] Environment variables set
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Firewall rules set
- [ ] Health checks working
- [ ] Performance optimized
- [ ] Security headers configured
- [ ] Error pages configured

## 📞 Support

For issues with Docker deployment:
1. Check logs: `./docker-deploy.sh logs`
2. Verify configuration: `./docker-deploy.sh status`
3. Restart services: `./docker-deploy.sh stop && ./docker-deploy.sh deploy`

Your marketing analytics dashboard is now ready for production deployment! 🚀 