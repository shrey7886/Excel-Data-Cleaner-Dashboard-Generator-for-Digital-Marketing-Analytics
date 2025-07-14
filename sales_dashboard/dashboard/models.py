from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    """Client model for managing different clients"""
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.company}"

    class Meta:
        ordering = ['name']


class Campaign(models.Model):
    """Campaign model for storing marketing campaign data"""
    PLATFORM_CHOICES = [
        ('mailchimp', 'Mailchimp'),
        ('zoho', 'Zoho'),
        ('demandbase', 'Demandbase'),
        ('google_ads', 'Google Ads'),
        ('linkedin_ads', 'LinkedIn Ads'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('draft', 'Draft'),
    ]

    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active'
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ctr = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cpm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0
    )
    cost_per_conversion = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    roi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='campaigns'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.platform}"

    class Meta:
        ordering = ['-created_at']


class CampaignReport(models.Model):
    """Report model for storing generated reports"""
    REPORT_TYPE_CHOICES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('custom', 'Custom Report'),
    ]

    REPORT_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
    ]

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='reports'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(
        upload_to='reports/', null=True, blank=True
    )
    report_format = models.CharField(
        max_length=10, choices=REPORT_FORMAT_CHOICES, default='pdf'
    )

    # KPI Summary
    total_impressions = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)
    total_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_ctr = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    avg_cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_cpm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0
    )
    cost_per_conversion = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    roi = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ML Predictions
    predicted_ctr = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    predicted_conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    predicted_revenue = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    confidence_score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )

    # Metadata
    is_public = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.campaign.name}"

    class Meta:
        ordering = ['-generated_at']


class UserProfile(models.Model):
    """Extended user profile for additional user information"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True,
        related_name='users'
    )
    role = models.CharField(max_length=50, default='viewer')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_client_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        ordering = ['user__username']


class MonthlySummary(models.Model):
    """Monthly summary reports for clients"""
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='monthly_summaries'
    )
    month = models.DateField()  # First day of the month
    created_at = models.DateTimeField(auto_now_add=True)

    # Summary Data
    total_campaigns = models.IntegerField(default=0)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_impressions = models.BigIntegerField(default=0)
    total_clicks = models.BigIntegerField(default=0)
    total_conversions = models.BigIntegerField(default=0)

    # Calculated Metrics
    overall_roas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_ctr = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    overall_conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0
    )
    avg_cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_cpm = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Platform Breakdown
    platform_data = models.JSONField(default=dict)

    # ML Insights
    ml_insights = models.JSONField(default=dict)

    # Report File
    report_file = models.FileField(
        upload_to='monthly_reports/', null=True, blank=True
    )

    # Status
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.client} - {self.month.strftime('%B %Y')}"

    class Meta:
        ordering = ['-month']
        unique_together = ['client', 'month']


class MLPrediction(models.Model):
    """Model for storing ML predictions and forecasts"""
    PREDICTION_TYPE_CHOICES = [
        ('campaign', 'Campaign Performance'),
        ('monthly_forecast', 'Monthly Forecast'),
        ('trend_analysis', 'Trend Analysis'),
        ('optimization', 'Optimization Recommendation'),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='ml_predictions',
        null=True, blank=True
    )
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='ml_predictions',
        null=True, blank=True
    )
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPE_CHOICES)

    # Prediction Data
    target_date = models.DateField(null=True, blank=True)  # For forecasts
    predicted_metrics = models.JSONField(default=dict)  # Store all predicted metrics
    confidence_score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )

    # Model Information
    model_used = models.CharField(max_length=50, default='ensemble')
    model_version = models.CharField(max_length=20, default='1.0')

    # Results
    insights = models.JSONField(default=list)  # List of insights
    recommendations = models.JSONField(default=list)  # List of recommendations

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.prediction_type} - {self.client or self.campaign}"

    class Meta:
        ordering = ['-created_at']


class FutureForecast(models.Model):
    """Model for storing future forecasts and predictions"""
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='future_forecasts'
    )
    forecast_date = models.DateField()  # The date being forecasted
    created_at = models.DateTimeField(auto_now_add=True)

    # Forecasted Metrics
    predicted_impressions = models.BigIntegerField(null=True, blank=True)
    predicted_clicks = models.BigIntegerField(null=True, blank=True)
    predicted_spend = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    predicted_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    predicted_conversions = models.BigIntegerField(null=True, blank=True)
    predicted_ctr = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    predicted_roi = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    # Confidence and Trend
    confidence_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.8
    )
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('increasing', 'Increasing'),
            ('decreasing', 'Decreasing'),
            ('stable', 'Stable'),
        ],
        default='stable'
    )
    trend_strength = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.5
    )

    # Additional Data
    seasonal_factors = models.JSONField(default=dict)
    market_conditions = models.JSONField(default=dict)
    risk_factors = models.JSONField(default=list)

    def __str__(self):
        return f"{self.client} - {self.forecast_date}"

    class Meta:
        ordering = ['-forecast_date']
        unique_together = ['client', 'forecast_date']


class ClientPrediction(models.Model):
    """Model for storing client-specific predictions based on unified data"""
    PREDICTION_TYPE_CHOICES = [
        ('monthly_forecast', 'Monthly Forecast'),
        ('campaign_performance', 'Campaign Performance'),
        ('revenue_prediction', 'Revenue Prediction'),
        ('optimization', 'Optimization'),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='predictions'
    )
    prediction_type = models.CharField(
        max_length=30, choices=PREDICTION_TYPE_CHOICES
    )

    # Prediction Details
    target_date = models.DateField(null=True, blank=True)  # For forecasts
    predicted_metrics = models.JSONField(default=dict)  # All predicted metrics
    confidence_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.8
    )

    # Model Information
    model_used = models.CharField(max_length=50, default='ensemble')
    model_version = models.CharField(max_length=20, default='1.0')

    # Results
    insights = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    risk_factors = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client} - {self.prediction_type}"

    class Meta:
        ordering = ['-created_at']


class GoogleAdsCredential(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='google_ads_credentials'
    )
    refresh_token = models.CharField(max_length=255)
    google_client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    developer_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - Google Ads"


class LinkedInAdsCredential(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='linkedin_ads_credentials'
    )
    access_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - LinkedIn Ads"


class MailchimpCredential(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='mailchimp_credentials'
    )
    api_key = models.CharField(max_length=255)
    server_prefix = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - Mailchimp"


class ZohoCredential(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='zoho_credentials'
    )
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    zoho_client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - Zoho"


class DemandbaseCredential(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='demandbase_credentials'
    )
    api_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - Demandbase"


class GoogleAdsData(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='google_ads_data'
    )
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - Google Ads Data"


class MailchimpData(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='mailchimp_data'
    )
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - Mailchimp Data"


class LinkedInAdsData(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='linkedin_ads_data'
    )
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - LinkedIn Ads Data"


class ZohoData(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='zoho_data'
    )
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - Zoho Data"


class DemandbaseData(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='demandbase_data'
    )
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - Demandbase Data"


class UnifiedClientData(models.Model):
    """Aggregated unified data summary for each client"""
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='unified_data'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('synced', 'Synced'),
            ('processing', 'Processing'),
            ('failed', 'Failed')
        ],
        default='synced'
    )
    total_records = models.IntegerField(default=0)
    date_range_start = models.DateField(blank=True, null=True)
    date_range_end = models.DateField(blank=True, null=True)
    platforms_included = models.JSONField(default=list)
    data_summary = models.JSONField(default=dict)  # KPIs, totals, etc.
    error_message = models.TextField(blank=True)
    processing_started_at = models.DateTimeField(blank=True, null=True)
    processing_completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.client} - {self.uploaded_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-uploaded_at']
        unique_together = ['client', 'date_range_start', 'date_range_end']


class ChatbotFeedback(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    query = models.TextField()
    answer = models.TextField()
    context = models.TextField()
    rating = models.IntegerField(null=True, blank=True)  # 1=upvote, -1=downvote, 0=neutral
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
