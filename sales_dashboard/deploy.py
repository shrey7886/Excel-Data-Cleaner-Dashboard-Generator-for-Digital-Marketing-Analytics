#!/usr/bin/env python3
"""
Deployment script for Marketing Analytics Dashboard
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'sales_dashboard/settings_production.py',
        'manage.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files found")
    return True

def collect_static():
    """Collect static files"""
    return run_command(
        "python manage.py collectstatic --noinput",
        "Collecting static files"
    )

def run_migrations():
    """Run database migrations"""
    return run_command(
        "python manage.py migrate",
        "Running database migrations"
    )

def create_superuser():
    """Create a superuser if needed"""
    print("👤 Do you want to create a superuser? (y/n): ", end="")
    response = input().lower()
    
    if response == 'y':
        return run_command(
            "python manage.py createsuperuser",
            "Creating superuser"
        )
    return True

def generate_secret_key():
    """Generate a new secret key"""
    import secrets
    return secrets.token_urlsafe(50)

def create_env_file():
    """Create .env file with production settings"""
    env_content = f"""# Production Environment Variables
SECRET_KEY={generate_secret_key()}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (will be set by hosting platform)
DATABASE_URL=sqlite:///db.sqlite3

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
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with production settings")
    print("⚠️  Remember to update the values for your specific deployment!")

def main():
    """Main deployment function"""
    print("🚀 Marketing Analytics Dashboard Deployment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Please run this script from the sales_dashboard directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create .env file
    if not Path('.env').exists():
        create_env_file()
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    print("\n🎉 Deployment preparation completed!")
    print("\n📋 Next steps:")
    print("1. Push your code to GitHub")
    print("2. Choose a hosting platform:")
    print("   - Railway (recommended): https://railway.app")
    print("   - Render: https://render.com")
    print("   - Heroku: https://heroku.com")
    print("   - PythonAnywhere: https://pythonanywhere.com")
    print("3. Set environment variables in your hosting platform")
    print("4. Deploy!")
    
    print("\n📖 For detailed instructions, see: deploy_guide.md")

if __name__ == "__main__":
    main() 