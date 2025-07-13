# Docker Deployment Guide for Targetorate

This guide covers multiple Docker deployment options for the Targetorate marketing analytics dashboard.

## 🐳 Quick Start (Local Development)

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd sales_dashboard
```

### 2. Create Environment File
```bash
cp env.example .env
# Edit .env with your production settings
```

### 3. Build and Run
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Setup Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Create sample data
# docker-compose exec web python manage.py create_sample_auth_data
```

### 5. Access Application
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin/
- Health check: http://localhost:8000/health/

## 🚀 Production Deployment Options

### Option 1: Docker Compose on VPS/Server

#### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Docker and Docker Compose
- Domain name (optional)

#### Deployment Steps

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

2. **Application Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd sales_dashboard

# Create production environment
cp env.example .env
nano .env  # Edit with production values
```

3. **Production Environment Variables**
```bash
# .env file
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost
DATABASE_URL=postgresql://postgres:postgres@db:5432/sales_dashboard
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

4. **Deploy**
```bash
# Build and start
docker-compose -f docker-compose.yml up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py createsuperuser

# Create sample data
# docker-compose exec web python manage.py create_sample_auth_data
```

5. **SSL Setup (Optional)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### Option 2: Docker Swarm (Multi-Node)

#### Setup Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Add worker nodes (on other servers)
docker swarm join --token <token> <manager-ip>:2377
```

#### Deploy Stack
```bash
# Deploy the stack
docker stack deploy -c docker-compose.yml targetorate

# Check services
docker service ls
```

### Option 3: Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (minikube, GKE, EKS, etc.)
- kubectl

#### Deploy to Kubernetes
```bash
# Apply configurations
kubectl apply -f k8s/

# Check pods
kubectl get pods

# Access application
kubectl port-forward svc/targetorate-web 8000:8000
```

## 🔧 Configuration Files

### Docker Compose Production
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=sales_dashboard
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery:
    build: .
    command: celery -A sales_dashboard worker --loglevel=info
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Check application health
curl http://localhost:8000/health/

# Check container status
docker-compose ps

# View logs
docker-compose logs -f web
```

### Backup Database
```bash
# Create backup
docker-compose exec db pg_dump -U postgres sales_dashboard > backup.sql

# Restore backup
docker-compose exec -T db psql -U postgres sales_dashboard < backup.sql
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files
- Use strong SECRET_KEY
- Set DEBUG=False in production
- Use HTTPS in production

### Database Security
- Change default PostgreSQL password
- Use strong database passwords
- Restrict database access

### Container Security
- Run containers as non-root user
- Keep base images updated
- Scan for vulnerabilities

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill process or change port
docker-compose down
```

2. **Database Connection Issues**
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

3. **Static Files Not Loading**
```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput
```

4. **Celery Worker Issues**
```bash
# Check celery logs
docker-compose logs celery

# Restart celery
docker-compose restart celery
```

### Performance Optimization

1. **Enable Caching**
```python
# settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}
```

2. **Database Optimization**
```bash
# Add database indexes
docker-compose exec web python manage.py dbshell
```

3. **Static File Optimization**
```bash
# Compress static files
docker-compose exec web python manage.py compress
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale web service
docker-compose up -d --scale web=3

# Scale celery workers
docker-compose up -d --scale celery=2
```

### Load Balancer
```yaml
# Add to docker-compose.yml
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
- Review this documentation
- Create GitHub issue
- Contact support team

---

**Happy Deploying! 🚀** 