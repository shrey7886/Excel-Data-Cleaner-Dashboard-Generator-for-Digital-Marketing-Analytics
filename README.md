# Excel Data Cleaner Dashboard Generator for Digital Marketing Analytics

A comprehensive Django-based SaaS platform for digital marketing analytics that allows clients to connect multiple marketing tools, view unified analytics, generate ML predictions, and download Excel dashboards.

## 🚀 Features

### Core Functionality
- **Multi-Platform Integration**: Connect Google Ads, LinkedIn Ads, Mailchimp, Zoho CRM, and Demandbase
- **Real-Time Analytics**: Unified dashboard showing KPIs from all connected platforms
- **ML Predictions**: Advanced machine learning models for CTR, conversion, and forecasting
- **Excel Dashboard Generation**: Professional Excel reports with charts, pivot tables, and predictions
- **Client Portal**: Secure client authentication and data management

### Technical Features
- **AJAX Real-Time Updates**: Dashboard refreshes without page reloads
- **Modern UI/UX**: Bootstrap-based responsive design with interactive elements
- **API Integrations**: OAuth and API key-based connections to marketing platforms
- **Background Processing**: Celery tasks for data synchronization
- **Production Ready**: Docker deployment with Nginx and Gunicorn

## 🛠️ Technology Stack

- **Backend**: Django 5.2.4, Python 3.11+
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Bootstrap 5, Chart.js, AJAX
- **ML/AI**: Scikit-learn, Prophet, XGBoost, Pandas, NumPy
- **Excel**: OpenPyXL for professional dashboard generation
- **Deployment**: Docker, Nginx, Gunicorn, Celery

## 📋 Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd Excel-Data-Cleaner-Dashboard-Generator-for-Digital-Marketing-Analytics
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Django
```bash
cd sales_dashboard
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📊 Platform Connections

### Google Ads
- OAuth 2.0 authentication
- Campaign performance data
- Keyword analytics
- Conversion tracking

### LinkedIn Ads
- API key authentication
- Campaign insights
- Audience analytics
- Lead generation data

### Mailchimp
- API key authentication
- Email campaign metrics
- Subscriber analytics
- Automation data

### Zoho CRM
- API token authentication
- Lead and contact data
- Sales pipeline analytics
- Customer insights

### Demandbase
- Account-based marketing data
- Company intelligence
- B2B analytics
- Intent data

## 🤖 Machine Learning Features

### Predictive Models
- **CTR Prediction**: Random Forest model for click-through rate forecasting
- **Conversion Prediction**: Logistic Regression for conversion probability
- **Time Series Forecasting**: Prophet models for trend analysis
- **Customer Segmentation**: K-means clustering for audience analysis

### Model Training
```bash
# Train CTR model
python ml/train_ctr_model.py

# Train conversion model
python ml/train_logistic_model.py

# Train forecasting models
python ml/forecast_prophet.py
```

## 📈 Dashboard Features

### Real-Time Analytics
- **Unified KPIs**: Cross-platform performance metrics
- **Platform Breakdown**: Individual tool analytics
- **Trend Analysis**: Historical data visualization
- **ML Insights**: AI-powered recommendations

### Excel Dashboard Generation
- **Professional Formatting**: Clean, branded reports
- **Interactive Charts**: Pivot tables and visualizations
- **Predictions Sheet**: ML forecast data
- **Automated Styling**: Consistent branding and formatting

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `sales_dashboard` directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# API Keys (for development)
GOOGLE_ADS_API_KEY=your-google-ads-api-key
LINKEDIN_ADS_API_KEY=your-linkedin-api-key
MAILCHIMP_API_KEY=your-mailchimp-api-key
ZOHO_API_KEY=your-zoho-api-key
```

### Production Deployment
```bash
# Build Docker image
docker build -t marketing-analytics-dashboard .

# Run with Docker Compose
docker-compose up -d
```

## 📁 Project Structure

```
├── api_integrations/          # Platform API integrations
├── ml/                       # Machine learning models and training
├── sales_dashboard/          # Django application
│   ├── dashboard/           # Main dashboard app
│   ├── sales_dashboard/     # Django settings
│   └── templates/          # HTML templates
├── src/                     # Data processing utilities
├── sample_data/            # Sample data for testing
├── input/                  # Input data files
├── output/                 # Generated Excel dashboards
└── requirements.txt        # Python dependencies
```

## 🔐 Security Features

- **User Authentication**: Django's built-in auth system
- **CSRF Protection**: Cross-site request forgery prevention
- **API Key Management**: Secure storage of platform credentials
- **Data Encryption**: Sensitive data protection
- **Session Management**: Secure user sessions

## 🧪 Testing

### Sample Data
The application includes sample data for testing:
- `sample_data/` - Test datasets for all platforms
- `input/` - Example marketing data files

### Running Tests
```bash
python manage.py test
```

## 📝 API Documentation

### Endpoints
- `/dashboard/` - Main dashboard
- `/dashboard/connect/` - Platform connection portal
- `/dashboard/sync-all/` - Data synchronization
- `/dashboard/generate-excel/` - Excel dashboard generation

### Authentication
All endpoints require user authentication except login/register pages.

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Deployment
```bash
# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Start production server
gunicorn sales_dashboard.wsgi:application
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the deployment guide in `sales_dashboard/README_DEPLOYMENT.md`

## 🔄 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Advanced ML model training interface
- [ ] Custom dashboard builder
- [ ] Multi-tenant architecture
- [ ] Advanced reporting features
- [ ] Mobile app development

---

**Built with ❤️ for Digital Marketing Analytics**
