#!/bin/bash

# Production Deployment Script for Sales Dashboard
# This script sets up and deploys the Django application

set -e  # Exit on any error

echo "🚀 Starting production deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from env.example"
    exit 1
fi

# Load environment variables
source .env

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p staticfiles
mkdir -p media
mkdir -p ssl

# Install system dependencies (Ubuntu/Debian)
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up PostgreSQL
echo "🐘 Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Run Django migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Set up Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/sales_dashboard
sudo ln -sf /etc/nginx/sites-available/sales_dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Set up systemd services
echo "🔧 Setting up systemd services..."

# Gunicorn service
sudo tee /etc/systemd/system/sales_dashboard.service > /dev/null <<EOF
[Unit]
Description=Sales Dashboard Gunicorn
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn --config gunicorn.conf.py sales_dashboard.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Celery worker service
sudo tee /etc/systemd/system/sales_dashboard_celery.service > /dev/null <<EOF
[Unit]
Description=Sales Dashboard Celery Worker
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/celery -A sales_dashboard worker -l info
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Celery beat service
sudo tee /etc/systemd/system/sales_dashboard_celerybeat.service > /dev/null <<EOF
[Unit]
Description=Sales Dashboard Celery Beat
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/celery -A sales_dashboard beat -l info
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable sales_dashboard
sudo systemctl enable sales_dashboard_celery
sudo systemctl enable sales_dashboard_celerybeat
sudo systemctl start sales_dashboard
sudo systemctl start sales_dashboard_celery
sudo systemctl start sales_dashboard_celerybeat

# Set up firewall
echo "🔥 Setting up firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Set up SSL certificate (Let's Encrypt)
echo "🔒 Setting up SSL certificate..."
if command -v certbot &> /dev/null; then
    sudo certbot --nginx -d $(hostname) --non-interactive --agree-tos --email admin@example.com
else
    echo "⚠️ Certbot not found. Please install it for SSL certificates."
fi

# Set proper permissions
echo "🔐 Setting proper permissions..."
sudo chown -R $USER:www-data .
sudo chmod -R 755 .
sudo chmod -R 775 media logs

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   - Main site: http://$(hostname)"
echo "   - Health check: http://$(hostname)/health/"
echo ""
echo "🔧 Management commands:"
echo "   - View logs: sudo journalctl -u sales_dashboard -f"
echo "   - Restart app: sudo systemctl restart sales_dashboard"
echo "   - Check status: sudo systemctl status sales_dashboard"
echo ""
echo "👤 Admin credentials:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo ""
echo "📝 Next steps:"
echo "   1. Update admin password"
echo "   2. Configure email settings"
echo "   3. Set up monitoring"
echo "   4. Configure backups" 