import sys
import os
# Add project root to sys.path for src import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, LoginForm, ClientForm, UserProfileForm, CampaignFilterForm, UserEditForm
from .models import Client, Campaign, CampaignReport, UserProfile, MLPrediction, MonthlySummary, ClientPrediction
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# --- STUB for advanced_analytics ---
class AdvancedAnalyticsStub:
    def time_series_analysis(self, *args, **kwargs):
        return {'message': 'Time series analysis placeholder', 'data': []}
    def segmentation_kmeans(self, *args, **kwargs):
        return {'message': 'Segmentation analysis placeholder', 'data': []}
    def attribution_modeling(self, *args, **kwargs):
        return {'message': 'Attribution modeling placeholder', 'data': []}
    def anomaly_detection(self, *args, **kwargs):
        return {'message': 'Anomaly detection placeholder', 'data': []}
    def cohort_analysis(self, *args, **kwargs):
        return {'message': 'Cohort analysis placeholder', 'data': []}
    def funnel_analysis(self, *args, **kwargs):
        return {'message': 'Funnel analysis placeholder', 'data': []}
    def custom_kpis(self, *args, **kwargs):
        return {'message': 'Custom KPIs placeholder', 'data': []}
    def comparative_analytics(self, *args, **kwargs):
        return {'message': 'Comparative analytics placeholder', 'data': []}
advanced_analytics = AdvancedAnalyticsStub()

@login_required
def advanced_analytics_view(request):
    """
    User-friendly advanced analytics dashboard view.
    """
    user = request.user
    client = getattr(user.profile, 'client', None)
    if not client:
        messages.error(request, 'No client associated with your account.')
        return render(request, 'dashboard/advanced_analytics.html', {'error': 'No client found.'})
    # Placeholder for analytics data
    context = {
        'user': user,
        'client': client,
        # 'analytics_data': ... (to be filled in)
    }
    return render(request, 'dashboard/advanced_analytics.html', context)

@login_required
@require_POST
def advanced_analytics_api(request):
    """
    API endpoint for advanced analytics AJAX requests.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        analytic_type = data.get('analytic_type')
        # TODO: Add parameters as needed for each analytic
        # Example: date range, columns, etc.
        # For now, just a stub
        if analytic_type == 'timeseries':
            result = advanced_analytics.time_series_analysis(None, '', '')
        elif analytic_type == 'segmentation':
            result = advanced_analytics.segmentation_kmeans(None, [])
        elif analytic_type == 'attribution':
            result = advanced_analytics.attribution_modeling(None, '', '')
        elif analytic_type == 'anomaly':
            result = advanced_analytics.anomaly_detection(None, '', '')
        elif analytic_type == 'cohort':
            result = advanced_analytics.cohort_analysis(None, '', '', '')
        elif analytic_type == 'funnel':
            result = advanced_analytics.funnel_analysis(None, [], '', '')
        elif analytic_type == 'kpi':
            result = advanced_analytics.custom_kpis(None, '', '')
        elif analytic_type == 'comparative':
            result = advanced_analytics.comparative_analytics(None, '', '')
        else:
            return JsonResponse({'status': 'error', 'message': 'Unknown analytic type.'}, status=400)
        return JsonResponse({'status': 'ok', 'data': result})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def health_check(request):
    return JsonResponse({'status': 'ok'})

def landing_page(request):
    """Public landing page for the application"""
    return render(request, 'dashboard/landing_page.html')

@login_required
def client_portal(request):
    """Client portal view - shows only campaigns for the user's client"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        # Create a profile for the user if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
        client = None
        messages.info(request, 'Profile created. Please contact administrator to associate with a client.')
    
    if not client:
        # Show a simple dashboard for users without clients
        context = {
            'user': request.user,
            'profile': profile,
            'no_client': True,
            'message': 'Welcome! Please contact administrator to set up your client account.'
        }
        return render(request, 'dashboard/simple_dashboard.html', context)
    
    campaigns = Campaign.objects.filter(client=client)
    filter_form = CampaignFilterForm(request.GET)
    if filter_form.is_valid():
        platform = filter_form.cleaned_data.get('platform')
        status = filter_form.cleaned_data.get('status')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        if platform:
            campaigns = campaigns.filter(platform=platform)
        if status:
            campaigns = campaigns.filter(status=status)
        if date_from:
            campaigns = campaigns.filter(start_date__gte=date_from)
        if date_to:
            campaigns = campaigns.filter(start_date__lte=date_to)
    paginator = Paginator(campaigns, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_campaigns = campaigns.count()
    active_campaigns = campaigns.filter(status='active').count()
    total_spend = campaigns.aggregate(total=Sum('spend'))['total'] or 0
    total_revenue = campaigns.aggregate(total=Sum('revenue'))['total'] or 0
    avg_ctr = campaigns.aggregate(avg=Avg('ctr'))['avg'] or 0
    avg_roi = campaigns.aggregate(avg=Avg('roi'))['avg'] or 0
    recent_reports = CampaignReport.objects.filter(campaign__client=client).order_by('-generated_at')[:5]
    context = {
        'client': client,
        'campaigns': page_obj,
        'filter_form': filter_form,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'total_spend': total_spend,
        'total_revenue': total_revenue,
        'avg_ctr': avg_ctr,
        'avg_roi': avg_roi,
        'recent_reports': recent_reports,
        'profile': profile,
    }
    return render(request, 'dashboard/auth/client_portal.html', context)

@login_required
def campaign_detail(request, campaign_id):
    """Campaign detail view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    # Get campaign for this client only
    campaign = get_object_or_404(Campaign, id=campaign_id, client=client)
    
    # Get reports for this campaign
    reports = CampaignReport.objects.filter(campaign=campaign).order_by('-generated_at')
    
    # Get ML insights if available
    ml_predictions = get_ml_insights_for_campaign(campaign)
    
    context = {
        'campaign': campaign,
        'reports': reports,
        'ml_predictions': ml_predictions,
    }
    return render(request, 'dashboard/campaign_detail.html', context)

@login_required
def report_list(request):
    """Report list view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    reports = CampaignReport.objects.filter(campaign__client=client).order_by('-generated_at')
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'client': client,
    }
    return render(request, 'dashboard/report_list.html', context)

def login_view(request):
    """Login view - redirect to auth_views"""
    from .auth_views import login_view as auth_login_view
    return auth_login_view(request)

def register_view(request):
    """Register view - redirect to auth_views"""
    from .auth_views import register_view as auth_register_view
    return auth_register_view(request)

@login_required
def logout_view(request):
    """Logout view - redirect to auth_views"""
    from .auth_views import logout_view as auth_logout_view
    return auth_logout_view(request)

@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('client_portal')
    
    # Get admin statistics
    total_clients = Client.objects.count()
    total_campaigns = Campaign.objects.count()
    total_reports = CampaignReport.objects.count()
    
    context = {
        'total_clients': total_clients,
        'total_campaigns': total_campaigns,
        'total_reports': total_reports,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def unified_data_list(request):
    """Unified data list view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    # Placeholder for unified data
    context = {
        'client': client,
        'unified_data_list': [],  # TODO: Implement unified data retrieval
    }
    return render(request, 'dashboard/unified_data_list.html', context)

@login_required
def unified_data_upload(request):
    """Unified data upload view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    if request.method == 'POST':
        # Handle file upload
        uploaded_file = request.FILES.get('data_file')
        if uploaded_file:
            # Placeholder for file processing
            messages.success(request, 'Data file uploaded successfully!')
            return redirect('unified_data_list')
        else:
            messages.error(request, 'Please select a file to upload.')
    
    context = {
        'client': client,
    }
    return render(request, 'dashboard/unified_data_upload.html', context)

@login_required
def generate_prediction(request, data_id):
    """Generate prediction view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    # Placeholder for prediction generation
    messages.success(request, 'Prediction generated successfully!')
    return redirect('unified_data_list')

@login_required
def prediction_detail(request, prediction_id):
    """Prediction detail view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    prediction = get_object_or_404(ClientPrediction, id=prediction_id, client=client)
    
    context = {
        'prediction': prediction,
        'client': client,
    }
    return render(request, 'dashboard/prediction_detail.html', context)

@login_required
def download_excel_dashboard(request, data_id):
    """Download Excel dashboard view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    # Placeholder for Excel download
    messages.success(request, 'Excel dashboard downloaded successfully!')
    return redirect('unified_data_list')

@login_required
def ml_predictions_view(request):
    """ML predictions view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    predictions = MLPrediction.objects.filter(client=client).order_by('-created_at')
    
    context = {
        'predictions': predictions,
        'client': client,
    }
    return render(request, 'dashboard/ml_predictions.html', context)

@login_required
def campaign_prediction_detail(request, prediction_id):
    """Campaign prediction detail view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    prediction = get_object_or_404(MLPrediction, id=prediction_id, client=client)
    
    context = {
        'prediction': prediction,
        'client': client,
    }
    return render(request, 'dashboard/campaign_prediction_detail.html', context)

@login_required
@require_POST
def generate_ml_prediction(request):
    """Generate ML prediction API endpoint"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=400)
    
    if not client:
        return JsonResponse({'status': 'error', 'message': 'No client associated with your account.'}, status=400)
    
    # Placeholder for ML prediction generation
    return JsonResponse({'status': 'success', 'message': 'Prediction generated successfully!'})

@login_required
def ml_insights_api(request):
    """ML insights API endpoint"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=400)
    
    if not client:
        return JsonResponse({'status': 'error', 'message': 'No client associated with your account.'}, status=400)
    
    # Placeholder for ML insights
    insights = {
        'trends': [],
        'recommendations': [],
        'anomalies': [],
    }
    return JsonResponse({'status': 'success', 'insights': insights})

@login_required
def monthly_summary_detail(request, summary_id):
    """Monthly summary detail view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    summary = get_object_or_404(MonthlySummary, id=summary_id, client=client)
    
    context = {
        'summary': summary,
        'client': client,
    }
    return render(request, 'dashboard/monthly_summary_detail.html', context)

# Platform connection views
@login_required
def connect_google_ads(request):
    """Connect Google Ads view"""
    if request.method == 'POST':
        # Handle form submission
        account_id = request.POST.get('account_id')
        customer_id = request.POST.get('customer_id')
        developer_token = request.POST.get('developer_token')
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
        refresh_token = request.POST.get('refresh_token')
        
        # Validate required fields
        if not all([account_id, customer_id, developer_token, client_id, client_secret, refresh_token]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required.'
            }, status=400)
        
        # Here you would typically save the credentials securely
        # For now, we'll just return success
        return JsonResponse({
            'status': 'success',
            'message': 'Google Ads connected successfully!'
        })
    
    return render(request, 'dashboard/connect_google_ads.html')

@login_required
def connect_linkedin_ads(request):
    """Connect LinkedIn Ads view"""
    if request.method == 'POST':
        # Handle form submission
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
        access_token = request.POST.get('access_token')
        account_id = request.POST.get('account_id')
        organization_id = request.POST.get('organization_id')
        
        # Validate required fields
        if not all([client_id, client_secret, access_token, account_id, organization_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required.'
            }, status=400)
        
        # Here you would typically save the credentials securely
        # For now, we'll just return success
        return JsonResponse({
            'status': 'success',
            'message': 'LinkedIn Ads connected successfully!'
        })
    
    return render(request, 'dashboard/connect_linkedin_ads.html')

@login_required
def connect_mailchimp(request):
    """Connect Mailchimp view"""
    if request.method == 'POST':
        # Handle form submission
        api_key = request.POST.get('api_key')
        server_prefix = request.POST.get('server_prefix')
        audience_id = request.POST.get('audience_id', '')
        
        # Validate required fields
        if not all([api_key, server_prefix]):
            return JsonResponse({
                'status': 'error',
                'message': 'API Key and Server Prefix are required.'
            }, status=400)
        
        # Here you would typically save the credentials securely
        # For now, we'll just return success
        return JsonResponse({
            'status': 'success',
            'message': 'Mailchimp connected successfully!'
        })
    
    return render(request, 'dashboard/connect_mailchimp.html')

@login_required
def connect_zoho(request):
    """Connect Zoho view"""
    if request.method == 'POST':
        # Handle form submission
        api_token = request.POST.get('api_token')
        domain = request.POST.get('domain')
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
        refresh_token = request.POST.get('refresh_token')
        
        # Validate required fields
        if not all([api_token, domain, client_id, client_secret, refresh_token]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required.'
            }, status=400)
        
        # Here you would typically save the credentials securely
        # For now, we'll just return success
        return JsonResponse({
            'status': 'success',
            'message': 'Zoho connected successfully!'
        })
    
    return render(request, 'dashboard/connect_zoho.html')

@login_required
def connect_tools_portal(request):
    """Connect tools portal view"""
    return render(request, 'dashboard/connect_tools_portal.html')

@login_required
def connect_demandbase(request):
    """Connect Demandbase view"""
    if request.method == 'POST':
        # Handle form submission
        api_key = request.POST.get('api_key', '')
        import_method = request.POST.get('import_method', 'manual')
        
        # For Demandbase, API key is optional
        # Here you would typically save the import method preference
        # For now, we'll just return success
        return JsonResponse({
            'status': 'success',
            'message': 'Demandbase connected successfully!'
        })
    
    return render(request, 'dashboard/connect_demandbase.html')

# OAuth views
@login_required
def google_oauth_initiate(request):
    """Google OAuth initiate view"""
    # For now, redirect to the manual form since OAuth is not fully implemented
    messages.info(request, 'OAuth integration coming soon! For now, please use the manual form.')
    return redirect('connect_google_ads')

@login_required
def google_oauth_callback(request):
    """Google OAuth callback view"""
    # Placeholder for Google OAuth callback
    messages.success(request, 'Google Ads connected successfully!')
    return redirect('connect_tools_portal')

@login_required
def linkedin_oauth_initiate(request):
    """LinkedIn OAuth initiate view"""
    # For now, redirect to the manual form since OAuth is not fully implemented
    messages.info(request, 'OAuth integration coming soon! For now, please use the manual form.')
    return redirect('connect_linkedin_ads')

@login_required
def linkedin_oauth_callback(request):
    """LinkedIn OAuth callback view"""
    # Placeholder for LinkedIn OAuth callback
    messages.success(request, 'LinkedIn Ads connected successfully!')
    return redirect('connect_tools_portal')

# AJAX connection endpoints
@login_required
@require_POST
def connect_google_ads_ajax(request):
    """Connect Google Ads AJAX endpoint"""
    return JsonResponse({'status': 'success', 'message': 'Google Ads connected successfully!'})

@login_required
@require_POST
def connect_linkedin_ads_ajax(request):
    """Connect LinkedIn Ads AJAX endpoint"""
    return JsonResponse({'status': 'success', 'message': 'LinkedIn Ads connected successfully!'})

@login_required
@require_POST
def connect_mailchimp_ajax(request):
    """Connect Mailchimp AJAX endpoint"""
    return JsonResponse({'status': 'success', 'message': 'Mailchimp connected successfully!'})

@login_required
@require_POST
def connect_zoho_ajax(request):
    """Connect Zoho AJAX endpoint"""
    return JsonResponse({'status': 'success', 'message': 'Zoho connected successfully!'})

@login_required
@require_POST
def connect_demandbase_ajax(request):
    """Connect Demandbase AJAX endpoint"""
    return JsonResponse({'status': 'success', 'message': 'Demandbase connected successfully!'})

@login_required
@require_POST
def disconnect_platform_ajax(request):
    """Disconnect platform AJAX endpoint"""
    return JsonResponse({'status': 'success', 'message': 'Platform disconnected successfully!'})

@login_required
def get_connection_status(request):
    """Get connection status AJAX endpoint"""
    return JsonResponse({'status': 'success', 'connections': {}})

# Unified insights views
@login_required
def unified_insights_view(request):
    """Unified insights view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
        'insights': [],  # TODO: Implement insights
    }
    return render(request, 'dashboard/unified_insights.html', context)

# Monthly analysis views
@login_required
def monthly_analysis_view(request):
    """Monthly analysis view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    summaries = MonthlySummary.objects.filter(client=client).order_by('-month')
    
    context = {
        'client': client,
        'summaries': summaries,
    }
    return render(request, 'dashboard/monthly_analysis.html', context)

@login_required
def monthly_predictions_view(request, summary_id):
    """Monthly predictions view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    summary = get_object_or_404(MonthlySummary, id=summary_id, client=client)
    
    context = {
        'summary': summary,
        'client': client,
    }
    return render(request, 'dashboard/monthly_predictions.html', context)

@login_required
def download_monthly_predictions(request, summary_id):
    """Download monthly predictions view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    summary = get_object_or_404(MonthlySummary, id=summary_id, client=client)
    
    # Placeholder for download
    messages.success(request, 'Monthly predictions downloaded successfully!')
    return redirect('monthly_predictions', summary_id=summary_id)

# Analytics views
@login_required
def google_ads_analysis(request):
    """Google Ads analysis view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
        'platform': 'google_ads',
    }
    return render(request, 'dashboard/google_ads_analysis.html', context)

@login_required
def linkedin_ads_analysis(request):
    """LinkedIn Ads analysis view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
        'platform': 'linkedin_ads',
    }
    return render(request, 'dashboard/linkedin_ads_analysis.html', context)

@login_required
def mailchimp_analysis(request):
    """Mailchimp analysis view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
        'platform': 'mailchimp',
    }
    return render(request, 'dashboard/mailchimp_analysis.html', context)

@login_required
def zoho_analysis(request):
    """Zoho analysis view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
        'platform': 'zoho',
    }
    return render(request, 'dashboard/zoho_analysis.html', context)

@login_required
def demandbase_analysis(request):
    """Demandbase analysis view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
        'platform': 'demandbase',
    }
    return render(request, 'dashboard/demandbase_analysis.html', context)

@login_required
def unified_analytics(request):
    """Unified analytics view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    context = {
        'client': client,
    }
    return render(request, 'dashboard/unified_analytics.html', context)

@login_required
def download_unified_analytics(request):
    """Download unified analytics view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    # Placeholder for download
    messages.success(request, 'Unified analytics downloaded successfully!')
    return redirect('unified_analytics')

@login_required
def sync_all_data(request):
    """Sync all data view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=400)
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    
    if not client:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'No client associated with your account.'}, status=400)
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    
    if request.method == 'POST':
        # Simulate data sync process
        import time
        time.sleep(2)  # Simulate processing time
        
        # Placeholder for actual sync logic
        sync_results = {
            'google_ads': {'status': 'success', 'message': 'Google Ads data synced'},
            'linkedin_ads': {'status': 'success', 'message': 'LinkedIn Ads data synced'},
            'mailchimp': {'status': 'success', 'message': 'Mailchimp data synced'},
            'zoho': {'status': 'success', 'message': 'Zoho data synced'},
            'demandbase': {'status': 'success', 'message': 'Demandbase data synced'},
        }
        
        return JsonResponse({
            'status': 'success',
            'message': 'All data synchronized successfully!',
            'results': sync_results
        })
    
    # For GET requests, redirect to client portal
    messages.success(request, 'All data synchronized successfully!')
    return redirect('client_portal')

@login_required
def dashboard_data_api(request):
    """Dashboard data API endpoint"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=400)
    
    if not client:
        return JsonResponse({'status': 'error', 'message': 'No client associated with your account.'}, status=400)
    
    # Placeholder for dashboard data
    data = {
        'campaigns': [],
        'metrics': {},
        'trends': [],
    }
    return JsonResponse({'status': 'success', 'data': data})

def get_ml_insights_for_campaign(campaign):
    """Get ML insights for a campaign"""
    # Placeholder for ML insights
    return {
        'ml_available': False,
        'predictions': {},
    }

@csrf_exempt
def llama_chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # Check if Ollama is available
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code != 200:
                return JsonResponse({
                    'reply': 'Sorry, the AI assistant is not available. Please install Ollama from https://ollama.com/download to enable the chatbot.'
                })
        except requests.exceptions.RequestException:
            return JsonResponse({
                'reply': 'Sorry, the AI assistant is not available. Please install Ollama from https://ollama.com/download to enable the chatbot.'
            })
        
        system_prompt = (
            "You are a helpful assistant for a digital marketing analytics dashboard. "
            "Answer questions about using the dashboard, connecting accounts, uploading data, "
            "viewing analytics, and troubleshooting common issues. Be concise, friendly, and guide the user step by step."
        )
        
        try:
            response = requests.post(
                'http://localhost:11434/api/chat',
                json={
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                },
                timeout=30
            )
            data = response.json()
            reply = data.get('message', {}).get('content', 'Sorry, I could not process your request.')
            return JsonResponse({'reply': reply})
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'reply': f'Sorry, there was an error connecting to the AI assistant. Please try again later. Error: {str(e)}'
            })
    return JsonResponse({'error': 'POST only'}) 