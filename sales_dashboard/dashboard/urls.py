from django.urls import path
from django.http import HttpResponse
from . import views

from . import auth_views

urlpatterns = [
    # Public landing page
    path('', views.landing_page, name='landing_page'),
    
    # Main views
    path('dashboard/', views.client_portal, name='client_portal'),
    path('campaign/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('reports/', views.report_list, name='report_list'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('client-portal/', views.client_portal, name='client_portal'),
    path('client-reports/', auth_views.client_reports_view, name='client_reports'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/clients/', auth_views.admin_clients_view, name='admin_clients'),
    path('admin/users/', auth_views.admin_users_view, name='admin_users'),
    
    # Unified Data Upload and Predictions
    path('unified-data/', views.unified_data_list, name='unified_data_list'),
    # path('unified-data/upload/', views.unified_data_upload, name='unified_data_upload'),
    path('generate-prediction/<int:data_id>/', views.generate_prediction, name='generate_prediction'),
    path('client-prediction/<int:prediction_id>/', views.prediction_detail, name='prediction_detail'),
    path('download-excel/<int:data_id>/', views.download_excel_dashboard, name='download_excel_dashboard'),
    
    # ML Predictions and Forecasts
    path('ml-predictions/', views.ml_predictions_view, name='ml_predictions'),
    path('campaign-prediction/<int:prediction_id>/', views.campaign_prediction_detail, name='campaign_prediction_detail'),
    path('api/generate-prediction/', views.generate_ml_prediction, name='generate_ml_prediction'),
    path('api/train-models/', views.train_ml_models, name='train_ml_models'),
    
    # API endpoints
    path('api/ml-insights/', views.ml_insights_api, name='ml_insights_api'),
    path('monthly-summary/<int:summary_id>/', views.monthly_summary_detail, name='monthly_summary_detail'),
    
    # Connect accounts
    path('connect/google-ads/', views.connect_google_ads, name='connect_google_ads'),
    path('connect/linkedin-ads/', views.connect_linkedin_ads, name='connect_linkedin_ads'),
    path('connect/mailchimp/', views.connect_mailchimp, name='connect_mailchimp'),
    path('connect/zoho/', views.connect_zoho, name='connect_zoho'),
    path('connect/tools/', views.connect_tools_portal, name='connect_tools_portal'),
    path('connect/demandbase/', views.connect_demandbase, name='connect_demandbase'),
    
    # OAuth endpoints
    path('oauth/google/initiate/', views.google_oauth_initiate, name='google_oauth_initiate'),
    path('oauth/google/callback/', views.google_oauth_callback, name='google_oauth_callback'),
    path('oauth/linkedin/initiate/', views.linkedin_oauth_initiate, name='linkedin_oauth_initiate'),
    path('oauth/linkedin/callback/', views.linkedin_oauth_callback, name='linkedin_oauth_callback'),
    
    # AJAX Connect/Disconnect endpoints
    path('api/connect/google-ads/', views.connect_google_ads_ajax, name='connect_google_ads_ajax'),
    path('api/connect/linkedin-ads/', views.connect_linkedin_ads_ajax, name='connect_linkedin_ads_ajax'),
    path('api/connect/mailchimp/', views.connect_mailchimp_ajax, name='connect_mailchimp_ajax'),
    path('api/connect/zoho/', views.connect_zoho_ajax, name='connect_zoho_ajax'),
    path('api/connect/demandbase/', views.connect_demandbase_ajax, name='connect_demandbase_ajax'),
    path('api/disconnect/', views.disconnect_platform_ajax, name='disconnect_platform_ajax'),
    path('api/connection-status/', views.get_connection_status, name='get_connection_status'),
    
    # Unified Insights
    path('unified-insights/', views.unified_insights_view, name='unified_insights'),
    
    # Monthly Analysis and Predictions
    path('monthly-analysis/', views.monthly_analysis_view, name='monthly_analysis'),
    path('monthly-predictions/<int:summary_id>/', views.monthly_predictions_view, name='monthly_predictions'),
    path('download-monthly-predictions/<int:summary_id>/', views.download_monthly_predictions, name='download_monthly_predictions'),
    
    # Analytics views
    path('analytics/google_ads/', views.google_ads_analysis, name='google_ads_analysis'),
    path('analytics/linkedin_ads/', views.linkedin_ads_analysis, name='linkedin_ads_analysis'),
    path('analytics/mailchimp/', views.mailchimp_analysis, name='mailchimp_analysis'),
    path('analytics/zoho/', views.zoho_analysis, name='zoho_analysis'),
    path('analytics/demandbase/', views.demandbase_analysis, name='demandbase_analysis'),
    path('analytics/unified/', views.unified_analytics, name='unified_analytics'),
    path('analytics/unified/download/', views.download_unified_analytics, name='download_unified_analytics'),
    
    # New URL pattern
    path('sync-all/', views.sync_all_data, name='sync_all_data'),
    
    # Added URL pattern
    path('dashboard/data/', views.dashboard_data_api, name='dashboard_data_api'),

    # Advanced Analytics
    path('advanced-analytics/', views.advanced_analytics_view, name='advanced_analytics'),
    # Advanced Analytics API
    path('api/advanced-analytics/', views.advanced_analytics_api, name='advanced_analytics_api'),
    
    # Chat functionality
    path('llama-chat/', views.llama_chat, name='llama_chat'),
] 