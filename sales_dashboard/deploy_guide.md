# 🚀 Deployment Guide for Marketing Analytics Dashboard

## Quick Deploy Options

### 1. **Railway (Recommended - Free & Easy)**

**Step 1: Prepare Your Code**
```bash
# Make sure you're in the sales_dashboard directory
cd sales_dashboard

# Create a .env file for local testing
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=False" >> .env
echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> .env
```

**Step 2: Deploy to Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect Django and deploy

**Step 3: Configure Environment Variables**
In Railway dashboard, add these environment variables:
```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app
DATABASE_URL=postgresql://... (Railway provides this)
```

### 2. **Render (Free Tier Available)**

**Step 1: Create render.yaml**
```yaml
services:
  - type: web
    name: marketing-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn sales_dashboard.wsgi:application
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: your-app-name.onrender.com
```

**Step 2: Deploy**
1. Go to [render.com](https://render.com)
2. Connect your GitHub repo
3. Create new Web Service
4. Render will auto-detect Django

### 3. **Heroku (Paid but Reliable)**

**Step 1: Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
heroku login
```

**Step 2: Deploy**
```bash
cd sales_dashboard
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
heroku run python manage.py migrate
```

### 4. **PythonAnywhere (Simple & Free)**

**Step 1: Sign Up**
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create free account
3. Go to "Web" tab

**Step 2: Upload Code**
1. Go to "Files" tab
2. Upload your project files
3. Or use Git: `git clone https://github.com/yourusername/your-repo.git`

**Step 3: Configure WSGI**
Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
```python
import os
import sys

path = '/home/yourusername/your-project-directory'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sales_dashboard.settings_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Production Checklist

### ✅ Before Deploying

1. **Update settings.py**
```python
# Change this line in settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings_production')
```

2. **Create superuser**
```bash
python manage.py createsuperuser
```

3. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

4. **Run migrations**
```bash
python manage.py migrate
```

### ✅ Environment Variables to Set

```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### ✅ Security Checklist

- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS
- [ ] Configure email settings
- [ ] Set up database backups
- [ ] Configure logging

## Domain & SSL

### Custom Domain Setup

1. **Buy a domain** (Namecheap, GoDaddy, etc.)
2. **Point DNS** to your hosting provider
3. **Add domain** to ALLOWED_HOSTS
4. **Configure SSL** (automatic on most platforms)

### SSL Certificate

Most platforms provide free SSL:
- **Railway**: Automatic HTTPS
- **Render**: Automatic SSL
- **Heroku**: Automatic SSL
- **PythonAnywhere**: Manual SSL setup

## Monitoring & Maintenance

### Health Checks

Add this to your main URL:
```python
# urls.py
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('health/', health_check, name='health_check'),
    # ... other URLs
]
```

### Logging

Configure logging in production:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Database connection errors**
   - Check DATABASE_URL format
   - Ensure database is created

3. **500 errors**
   - Check logs in hosting platform
   - Verify ALLOWED_HOSTS
   - Check SECRET_KEY

4. **Chatbot not working**
   - Ollama needs to be installed on server
   - Or use cloud-based AI service

## Cost Comparison

| Platform | Free Tier | Paid Plans | Ease of Use |
|----------|-----------|------------|-------------|
| Railway | ✅ Yes | $5/month | ⭐⭐⭐⭐⭐ |
| Render | ✅ Yes | $7/month | ⭐⭐⭐⭐ |
| Heroku | ❌ No | $7/month | ⭐⭐⭐ |
| PythonAnywhere | ✅ Yes | $5/month | ⭐⭐⭐⭐ |

## Recommended: Railway

**Why Railway is best for your project:**
- ✅ Free tier available
- ✅ Automatic Django detection
- ✅ Built-in PostgreSQL
- ✅ Automatic HTTPS
- ✅ Easy environment variables
- ✅ Great documentation

**Deploy in 5 minutes:**
1. Push code to GitHub
2. Connect Railway to GitHub
3. Add environment variables
4. Deploy!

Your dashboard will be live at: `https://your-app-name.railway.app` 