# 🐳 Quick Docker Deployment Guide

## Prerequisites

1. **Install Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
   - Download from: https://www.docker.com/products/docker-desktop/
   - For Linux: `curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh`

2. **Install Docker Compose** (usually included with Docker Desktop)
   - For Linux: `sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose`

## 🚀 Quick Start

### Step 1: Clone and Navigate
```bash
git clone <your-repo-url>
cd sales_dashboard
```

### Step 2: Create Environment File
```bash
# Copy environment template
cp env.example .env

# Edit with your settings (optional for local development)
# nano .env
```

### Step 3: Deploy with One Command

**Windows:**
```cmd
docker-deploy.bat deploy
```

**Linux/Mac:**
```bash
./docker-deploy.sh deploy
```

### Step 4: Access Your Application
- **Main Site**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

## 📋 Management Commands

### Windows Commands
```cmd
# Start services
docker-deploy.bat start

# Stop services
docker-deploy.bat stop

# View logs
docker-deploy.bat logs

# Check status
docker-deploy.bat status

# Create backup
docker-deploy.bat backup

# Update application
docker-deploy.bat update

# Clean up everything
docker-deploy.bat cleanup
```

### Linux/Mac Commands
```bash
# Start services
./docker-deploy.sh start

# Stop services
./docker-deploy.sh stop

# View logs
./docker-deploy.sh logs

# Check status
./docker-deploy.sh status

# Create backup
./docker-deploy.sh backup

# Update application
./docker-deploy.sh update

# Clean up everything
./docker-deploy.sh cleanup
```

## 🔧 Manual Docker Commands

If you prefer manual control:

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## 🌐 Production Deployment

### Option 1: VPS/Server
1. SSH into your server
2. Install Docker: `curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh`
3. Clone repository
4. Edit `.env` with production settings
5. Run: `./docker-deploy.sh deploy prod`

### Option 2: Cloud Platforms
- **AWS**: Use ECS/Fargate
- **Google Cloud**: Use Cloud Run
- **Azure**: Use Container Instances
- **DigitalOcean**: Use App Platform

### Option 3: Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check pods
kubectl get pods

# Access application
kubectl port-forward svc/targetorate-web 8000:8000
```

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY in .env
- [ ] Configure HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure monitoring
- [ ] Set up log rotation

## 🚨 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000
   
   # Stop conflicting service or change port in docker-compose.yml
   ```

2. **Database connection failed**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

3. **Static files not loading**
   ```bash
   # Recollect static files
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. **Memory issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   ```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health/

# Check all services
docker-compose ps

# View resource usage
docker stats
```

## 📊 Monitoring

### Basic Monitoring
```bash
# View logs in real-time
docker-compose logs -f

# Monitor resource usage
docker stats

# Check service status
docker-compose ps
```

### Advanced Monitoring
- Set up Prometheus + Grafana
- Configure log aggregation (ELK stack)
- Set up alerting
- Monitor database performance

## 🔄 Updates

### Update Application
```bash
# Pull latest changes
git pull origin main

# Update with deployment script
./docker-deploy.sh update
# or
docker-deploy.bat update
```

### Update Dependencies
```bash
# Rebuild with latest dependencies
docker-compose build --no-cache
docker-compose up -d
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale web services
docker-compose up -d --scale web=3

# Scale celery workers
docker-compose up -d --scale celery=2
```

### Load Balancer
Add nginx service to docker-compose.yml:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - web
```

## 🎯 Next Steps

1. **Set up monitoring** (Prometheus, Grafana)
2. **Configure backups** (automated database backups)
3. **Set up CI/CD** (GitHub Actions, GitLab CI)
4. **Add SSL certificates** (Let's Encrypt)
5. **Configure email** (SMTP settings)
6. **Set up logging** (ELK stack)

## 📞 Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review documentation: `DOCKER_DEPLOYMENT.md`
- Create GitHub issue
- Contact support team

---

**Happy Deploying! 🚀** 