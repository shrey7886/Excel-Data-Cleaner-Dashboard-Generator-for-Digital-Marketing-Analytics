
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime
import requests
from .models import (
    Campaign, CampaignReport, Client, UserProfile,
    MLPrediction, MonthlySummary, ClientPrediction,
    GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, 
    DemandbaseData, ChatbotFeedback
)
from .forms import CampaignFilterForm
import json
# from dashboard.rag_pipeline import rag_answer
from django.core.cache import cache
from django.conf import settings
from functools import wraps
from time import time
import logging
logger = logging.getLogger(__name__)


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
        messages.info(
            request,
            'Profile created. Please contact administrator to associate with a client.'
        )

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

    # If no campaigns exist, do NOT create a sample campaign
    # Just show an empty dashboard or a neutral message

    paginator = Paginator(campaigns, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_campaigns = campaigns.count()
    active_campaigns = campaigns.filter(status='active').count()
    total_spend = campaigns.aggregate(total=Sum('spend'))['total'] or 0
    total_revenue = campaigns.aggregate(total=Sum('revenue'))['total'] or 0
    avg_ctr = campaigns.aggregate(avg=Avg('ctr'))['avg'] or 0
    avg_roi = campaigns.aggregate(avg=Avg('roi'))['avg'] or 0
    recent_reports = CampaignReport.objects.filter(
        campaign__client=client
    ).order_by('-generated_at')[:5]

    # Create platform connections status (placeholder for now)
    platform_connections = {
        'google_ads': False,
        'linkedin_ads': False,
        'mailchimp': False,
        'zoho': False,
        'demandbase': False,
    }

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
        'platform_connections': platform_connections,
        'current_month_summary': None,  # Placeholder
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
    try:
        campaign = Campaign.objects.get(id=campaign_id, client=client)
    except Campaign.DoesNotExist:
        messages.error(request, 'Campaign not found.')
        return redirect('client_portal')

    # Get reports for this campaign
    reports = CampaignReport.objects.filter(
        campaign=campaign
    ).order_by('-generated_at')

    # If no reports exist, do NOT create a sample report
    # Just show an empty table or a neutral message

    # Get ML insights if available (placeholder for now)
    ml_predictions = None

    context = {
        'campaign': campaign,
        'reports': reports,
        'ml_predictions': ml_predictions,
        'client': client,
        'profile': profile,
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

    # Get reports for this client
    reports = CampaignReport.objects.filter(
        campaign__client=client
    ).order_by('-generated_at')

    # If no reports exist, do NOT create sample reports or campaigns
    # Just show an empty table or a neutral message

    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reports': page_obj,
        'client': client,
        'total_reports': reports.count(),
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

    clients = Client.objects.all()
    total_campaigns = Campaign.objects.count()
    total_reports = CampaignReport.objects.count()
    total_predictions = MLPrediction.objects.count()

    context = {
        'clients': clients,
        'total_campaigns': total_campaigns,
        'total_reports': total_reports,
        'total_predictions': total_predictions,
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

    # Get unified data for this client
    from .models import UnifiedClientData
    data_list = UnifiedClientData.objects.filter(
        client=client
    ).order_by('-uploaded_at')

    context = {
        'data_list': data_list,
        'client': client,
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
            # Process the uploaded file
            messages.success(request, 'Data uploaded successfully!')
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

    # Get the data for this client
    from .models import UnifiedClientData
    get_object_or_404(UnifiedClientData, id=data_id, client=client)

    context = {
        'client': client,
    }
    return render(request, 'dashboard/generate_prediction.html', context)


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

    # Get prediction for this client
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

    # Get the data for this client
    from .models import UnifiedClientData
    get_object_or_404(UnifiedClientData, id=data_id, client=client)

    # Generate Excel dashboard
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

    # Get ML predictions for this client
    predictions = MLPrediction.objects.filter(
        campaign__client=client
    ).order_by('-created_at')

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

    # Get prediction for this client
    prediction = get_object_or_404(
        MLPrediction, id=prediction_id, campaign__client=client
    )

    context = {
        'prediction': prediction,
        'client': client,
    }
    return render(request, 'dashboard/campaign_prediction_detail.html', context)


@login_required
@require_POST
def generate_ml_prediction(request):
    """Generate ML prediction view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'User profile not found.'}, status=400
        )

    if not client:
        return JsonResponse(
            {'status': 'error', 'message': 'No client associated with your account.'},
            status=400
        )

    # Generate ML prediction
    return JsonResponse({'status': 'success', 'message': 'Prediction generated!'})


@login_required
def ml_insights_api(request):
    """ML insights API endpoint"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'User profile not found.'}, status=400
        )

    if not client:
        return JsonResponse(
            {'status': 'error', 'message': 'No client associated with your account.'},
            status=400
        )

    # Get ML insights
    insights = get_ml_insights_for_client(client)
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

    # Get summary for this client
    summary = get_object_or_404(MonthlySummary, id=summary_id, client=client)

    context = {
        'summary': summary,
        'client': client,
    }
    return render(request, 'dashboard/monthly_summary_detail.html', context)


@login_required
def connect_google_ads(request):
    """Connect Google Ads view"""
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
    return render(request, 'dashboard/connect_google_ads.html', context)


@login_required
def connect_linkedin_ads(request):
    """Connect LinkedIn Ads view"""
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
    return render(request, 'dashboard/connect_linkedin_ads.html', context)


@login_required
def connect_mailchimp(request):
    """Connect Mailchimp view"""
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
    return render(request, 'dashboard/connect_mailchimp.html', context)


@login_required
def connect_zoho(request):
    """Connect Zoho view"""
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
    return render(request, 'dashboard/connect_zoho.html', context)


@login_required
def connect_tools_portal(request):
    """Connect tools portal view"""
    return render(request, 'dashboard/connect_tools_portal.html')


@login_required
def connect_demandbase(request):
    """Connect Demandbase view"""
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
    return render(request, 'dashboard/connect_demandbase.html', context)


@login_required
def google_oauth_initiate(request):
    """Google OAuth initiate view"""
    # Render a friendly page instead of JSON
    return render(request, 'dashboard/oauth_coming_soon.html', {
        'platform': 'Google Ads',
        'manual_url': '/connect/google-ads/'
    })


@login_required
def google_oauth_callback(request):
    """Google OAuth callback view"""
    # OAuth callback implementation
    return JsonResponse({'status': 'success', 'message': 'OAuth completed'})


@login_required
def linkedin_oauth_initiate(request):
    """LinkedIn OAuth initiate view"""
    # OAuth implementation
    return JsonResponse({'status': 'success', 'message': 'OAuth initiated'})


@login_required
def linkedin_oauth_callback(request):
    """LinkedIn OAuth callback view"""
    # OAuth callback implementation
    return JsonResponse({'status': 'success', 'message': 'OAuth completed'})


@login_required
@require_POST
def connect_google_ads_ajax(request):
    """Connect Google Ads AJAX view"""
    return JsonResponse({'status': 'success', 'message': 'Connected successfully'})


@login_required
@require_POST
def connect_linkedin_ads_ajax(request):
    """Connect LinkedIn Ads AJAX view"""
    return JsonResponse({'status': 'success', 'message': 'Connected successfully'})


@login_required
@require_POST
def connect_mailchimp_ajax(request):
    """Connect Mailchimp AJAX view"""
    return JsonResponse({'status': 'success', 'message': 'Connected successfully'})


@login_required
@require_POST
def connect_zoho_ajax(request):
    """Connect Zoho AJAX view"""
    return JsonResponse({'status': 'success', 'message': 'Connected successfully'})


@login_required
@require_POST
def connect_demandbase_ajax(request):
    """Connect Demandbase AJAX view"""
    return JsonResponse({'status': 'success', 'message': 'Connected successfully'})


@login_required
@require_POST
def disconnect_platform_ajax(request):
    """Disconnect platform AJAX view"""
    return JsonResponse({'status': 'success', 'message': 'Disconnected successfully'})


@login_required
def get_connection_status(request):
    """Get connection status view"""
    return JsonResponse({'status': 'success', 'connections': {}})


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

    get_object_or_404(MonthlySummary, id=summary_id, client=client)

    context = {
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
            return JsonResponse(
                {'status': 'error', 'message': 'User profile not found.'}, status=400
            )
        messages.error(request, 'User profile not found.')
        return redirect('client_portal')
    if not client:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'status': 'error', 'message': 'No client associated with your account.'},
                status=400
            )
        messages.error(request, 'No client associated with your account.')
        return redirect('client_portal')
    if request.method == 'POST':
        # Call real sync logic for each integration
        sync_results = sync_all_integrations_for_client(client)  # Implement this for real integrations
        return JsonResponse({
            'status': 'success',
            'message': 'All data synchronized successfully!' if sync_results else 'No data available from integrations.',
            'results': sync_results or {},
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
        return JsonResponse(
            {'status': 'error', 'message': 'User profile not found.'}, status=400
        )
    if not client:
        return JsonResponse(
            {'status': 'error', 'message': 'No client associated with your account.'},
            status=400
        )
    # Only real dashboard data from integrations
    dashboard_data = get_real_dashboard_data(client)  # Implement this to fetch real data
    if not dashboard_data:
        return JsonResponse(
            {'status': 'success', 'data': None, 'message': 'No data available from connected tools.'}
        )
    return JsonResponse({'status': 'success', 'data': dashboard_data})


def get_ml_insights_for_campaign(campaign):
    """Get ML insights for a specific campaign"""
    try:
        # Only return real ML insights if available
        ml_insights = fetch_real_ml_insights(campaign)  # Implement this for real ML
        if not ml_insights:
            return {
                'ml_available': False,
                'message': 'No ML insights available for this campaign.'
            }
        return ml_insights
    except Exception as e:
        return {
            'ml_available': False,
            'error': str(e)
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


# --- Rate Limiting Decorator ---
def rate_limit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        ident = f'user_{user.id}' if user else f'ip_{request.META.get("REMOTE_ADDR")}'
        key = f'rag_rate_{ident}'
        window = 60  # seconds
        limit = getattr(settings, 'RAG_RATE_LIMIT', 5)
        now = int(time())
        bucket = cache.get(key, {'count': 0, 'start': now})
        if now - bucket['start'] >= window:
            bucket = {'count': 0, 'start': now}
        bucket['count'] += 1
        cache.set(key, bucket, timeout=window)
        if bucket['count'] > limit:
            return JsonResponse({'error': 'Rate limit exceeded. Please wait before sending more queries.'}, status=429)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# @csrf_exempt
# @rate_limit
# def rag_chatbot(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)
#         query = data.get("query", "")
#         history = data.get("history", [])
#         user = request.user if request.user.is_authenticated else None
#         user_ident = user.username if user else request.META.get("REMOTE_ADDR")
#         if not query:
#             logger.warning(f"[RAG] No query provided by {user_ident}")
#             return JsonResponse({"error": "No query provided."}, status=400)
#         try:
#             context_chunks = retrieve_context(query)
#             answer = rag_answer(query, history=history)
#             ChatbotFeedback.objects.create(
#                 user=user,
#                 query=query,
#                 answer=answer,
#                 context='\n'.join(context_chunks),
#                 rating=None
#             )
#             logger.info(f"[RAG] Query by {user_ident}: '{query}' | Answer: '{answer[:100]}...'")
#             return JsonResponse({"answer": answer, "context": context_chunks})
#         except Exception as e:
#             logger.error(f"[RAG] Error processing query by {user_ident}: {e}")
#             return JsonResponse({"error": "Internal server error."}, status=500)
#     return JsonResponse({"error": "POST only."}, status=405)

@csrf_exempt
def chatbot_feedback(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        feedback_id = data.get("feedback_id")
        rating = data.get("rating")
        if feedback_id is None or rating not in [-1, 0, 1]:
            logger.warning(f"[RAG] Invalid feedback: {data}")
            return JsonResponse({"error": "Invalid feedback."}, status=400)
        try:
            feedback = ChatbotFeedback.objects.get(id=feedback_id)
            feedback.rating = rating
            feedback.save()
            logger.info(f"[RAG] Feedback received: id={feedback_id}, rating={rating}")
            return JsonResponse({"status": "success"})
        except ChatbotFeedback.DoesNotExist:
            logger.error(f"[RAG] Feedback not found: id={feedback_id}")
            return JsonResponse({"error": "Feedback not found."}, status=404)
    return JsonResponse({"error": "POST only."}, status=405)


@login_required
@require_POST
def train_ml_models(request):
    """Trigger automatic ML model training"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'User profile not found.'}, status=400
        )

    if not client:
        return JsonResponse(
            {'status': 'error', 'message': 'No client associated with your account.'},
            status=400
        )

    # Import ML service
    from .services import ml_service

    # Train models
    success = ml_service.auto_train_models(client.id)

    if success:
        return JsonResponse({
            'status': 'success',
            'message': 'ML models trained successfully!',
            'accuracy': ml_service.model_accuracy,
            'last_training': ml_service.last_training_date.isoformat() if ml_service.last_training_date else None
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Model training failed. Need at least 10 campaigns with sufficient data.'
        }, status=400)


# --- Real Data Aggregation Functions ---
def get_real_dashboard_data(client):
    """Aggregate dashboard data only from Google Ads, LinkedIn, Mailchimp, Zoho, and Demandbase for the given client."""
    all_data = []
    for model in [GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, DemandbaseData]:
        tool_data = model.objects.filter(client=client).order_by('-fetched_at')
        for entry in tool_data:
            entry_data = entry.data if isinstance(entry.data, list) else [entry.data] if isinstance(entry.data, dict) else []
            all_data.extend(entry_data)
    # Aggregate KPIs
    kpis = {'impressions': 0, 'clicks': 0, 'spend': 0, 'revenue': 0}
    for record in all_data:
        for k in kpis:
            try:
                kpis[k] += float(record.get(k, 0) or 0)
            except Exception:
                continue
    return {'kpis': kpis, 'records': all_data}


def get_real_advanced_analytics(client):
    """Perform advanced analytics only on data from the five tools for the given client, and return actionable insights."""
    dashboard_data = get_real_dashboard_data(client)
    records = dashboard_data['records']
    kpis = dashboard_data['kpis']
    insights = []
    if not records:
        return {
            'summary': kpis,
            'record_count': 0,
            'insights': [],
        }
    # --- Compute trends ---
    # Group by platform
    from collections import defaultdict
    platform_stats = defaultdict(lambda: {
        'impressions': 0, 'clicks': 0, 'spend': 0, 'revenue': 0,
        'conversions': 0, 'dates': [], 'roi': 0, 'ctr': 0
    })
    for r in records:
        platform = r.get('platform', 'unknown')
        platform_stats[platform]['impressions'] += float(r.get('impressions', 0) or 0)
        platform_stats[platform]['clicks'] += float(r.get('clicks', 0) or 0)
        platform_stats[platform]['spend'] += float(r.get('spend', 0) or 0)
        platform_stats[platform]['revenue'] += float(r.get('revenue', 0) or 0)
        platform_stats[platform]['conversions'] += float(r.get('conversions', 0) or 0)
        if r.get('date'):
            platform_stats[platform]['dates'].append(r['date'])
    # Calculate derived metrics
    for p, stats in platform_stats.items():
        stats['ctr'] = (stats['clicks'] / stats['impressions']) if stats['impressions'] > 0 else 0
        stats['roi'] = (stats['revenue'] / stats['spend']) if stats['spend'] > 0 else 0
    # Best/worst performing platform
    best_platform = max(
        platform_stats.items(),
        key=lambda x: x[1]['roi'] if x[1]['spend'] > 0 else -1,
        default=(None, None)
    )[0]
    worst_platform = min(
        platform_stats.items(),
        key=lambda x: x[1]['roi'] if x[1]['spend'] > 0 else float('inf'),
        default=(None, None)
    )[0]
    # Spend efficiency
    if best_platform:
        insights.append({
            'type': 'opportunity',
            'title': f'Best Performing Platform: {best_platform}',
            'description': f'{best_platform} has the highest ROI of {platform_stats[best_platform]["roi"]:.2f}. Consider increasing budget allocation.',
            'priority': 'high',
        })
    if worst_platform and platform_stats[worst_platform]['spend'] > 0:
        insights.append({
            'type': 'warning',
            'title': f'Least Efficient Platform: {worst_platform}',
            'description': f'{worst_platform} has the lowest ROI of {platform_stats[worst_platform]["roi"]:.2f}. Review campaign strategy or reduce spend.',
            'priority': 'medium',
        })
    # Conversion rate
    total_conversions = sum(stats['conversions'] for stats in platform_stats.values())
    total_clicks = sum(stats['clicks'] for stats in platform_stats.values())
    conversion_rate = (total_conversions / total_clicks) if total_clicks > 0 else 0
    insights.append({
        'type': 'metric',
        'title': 'Overall Conversion Rate',
        'description': f'Your overall conversion rate is {conversion_rate:.2%}.',
        'priority': 'info',
    })
    # Spend trend (last 30 days vs previous 30 days)
    today = datetime.today().date()
    last_30 = [
        r for r in records if r.get('date') and
        (today - datetime.strptime(r['date'], '%Y-%m-%d').date()).days <= 30
    ]
    prev_30 = [
        r for r in records if r.get('date') and
        30 < (today - datetime.strptime(r['date'], '%Y-%m-%d').date()).days <= 60
    ]
    spend_last_30 = sum(float(r.get('spend', 0) or 0) for r in last_30)
    spend_prev_30 = sum(float(r.get('spend', 0) or 0) for r in prev_30)
    if spend_prev_30 > 0:
        spend_trend = (spend_last_30 - spend_prev_30) / spend_prev_30
        trend_desc = 'increased' if spend_trend > 0 else 'decreased'
        insights.append({
            'type': 'trend',
            'title': 'Spend Trend',
            'description': f'Your spend has {trend_desc} by {abs(spend_trend):.2%} compared to the previous month.',
            'priority': 'info',
        })
    # ML predictions (if available)
    from .models import Campaign
    from .services import ml_service
    ml_insights = []
    for campaign in Campaign.objects.filter(client=client):
        ml_result = ml_service.predict_campaign_performance({
            'impressions': campaign.impressions,
            'clicks': campaign.clicks,
            'spend': campaign.spend,
            'budget': campaign.budget,
            'platform': campaign.platform,
            'status': campaign.status,
            'days_running': (campaign.end_date - campaign.start_date).days if campaign.end_date and campaign.start_date else 30,
            'ctr': float(campaign.ctr),
            'cpc': float(campaign.cpc),
            'cpm': float(campaign.cpm),
        })
        if ml_result and ml_result.get('ml_available'):
            ml_insights.append({
                'campaign': campaign.name,
                'predictions': ml_result.get('predictions'),
                'insights': ml_result.get('insights'),
            })
    return {
        'summary': kpis,
        'record_count': len(records),
        'insights': insights,
        'platform_stats': dict(platform_stats),
        'ml_insights': ml_insights,
    }


def fetch_real_ml_insights(campaign):
    """Run ML predictions only on campaign data from the five tools."""
    from .services import ml_service
    # The campaign object should already be from the correct client and platform
    campaign_data = {
        'impressions': campaign.impressions,
        'clicks': campaign.clicks,
        'spend': campaign.spend,
        'budget': campaign.budget,
        'platform': campaign.platform,
        'status': campaign.status,
        'days_running': (campaign.end_date - campaign.start_date).days if campaign.end_date and campaign.start_date else 30,
        'ctr': float(campaign.ctr),
        'cpc': float(campaign.cpc),
        'cpm': float(campaign.cpm),
    }
    return ml_service.predict_campaign_performance(campaign_data)


def get_ml_insights_for_client(client):
    """Get ML insights for a client"""
    # Placeholder implementation
    return {'ml_available': False, 'message': 'No ML insights available.'}


def sync_all_integrations_for_client(client):
    """Sync all integrations for a client"""
    # Placeholder implementation
    return {'status': 'success', 'message': 'All integrations synced successfully.'} 


@login_required
def advanced_analytics_view(request):
    """Advanced analytics view"""
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
    return render(request, 'dashboard/advanced_analytics.html', context)


@login_required
@require_POST
def advanced_analytics_api(request):
    """Advanced analytics API endpoint"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'User profile not found.'}, status=400
        )

    if not client:
        return JsonResponse(
            {'status': 'error', 'message': 'No client associated with your account.'},
            status=400
        )

    try:
        data = json.loads(request.body)
        analytic_type = data.get('analytic_type')
        
        if not analytic_type:
            return JsonResponse(
                {'status': 'error', 'message': 'Analytic type is required.'}, status=400
            )

        # Get real advanced analytics data
        analytics_data = get_real_advanced_analytics(client)
        
        if not analytics_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No analytics data available for this client.'
            }, status=404)

        return JsonResponse({
            'status': 'ok',
            'data': analytics_data.get(analytic_type, {}),
            'analytic_type': analytic_type
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid JSON data.'}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': f'Error processing request: {str(e)}'}, status=500
        ) 



