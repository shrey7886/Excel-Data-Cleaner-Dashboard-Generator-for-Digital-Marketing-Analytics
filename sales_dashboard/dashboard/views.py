from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.contrib.auth.models import User
from .models import Campaign, CampaignReport, Client, UserProfile, MonthlySummary, MLPrediction, FutureForecast, ClientPrediction, GoogleAdsData, MailchimpData, LinkedInAdsData, ZohoData, GoogleAdsCredential, LinkedInAdsCredential, MailchimpCredential, ZohoCredential, DemandbaseCredential, DemandbaseData
from .forms import UserRegistrationForm, UserProfileForm, GoogleAdsCredentialForm, LinkedInAdsCredentialForm, MailchimpCredentialForm, ZohoCredentialForm
from .services import ml_service
from .excel_dashboard_generator import ExcelDashboardGenerator
import json
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
import os
import io
from api_integrations.mailchimp import fetch_mailchimp_data
from api_integrations.google_ads import fetch_google_ads_data
from api_integrations.linkedin_ads import fetch_linkedin_ads_data
from api_integrations.zoho import fetch_zoho_data
from api_integrations.demandbase import fetch_demandbase_data
from django.conf import settings
import requests
from urllib.parse import urlencode
import secrets

logger = logging.getLogger(__name__)

def health_check(request):
    """Health check endpoint for monitoring."""
    return HttpResponse("healthy", content_type="text/plain")

@login_required
def dashboard(request):
    """Main dashboard view (refactored for per-platform data)."""
    try:
        # Get user's client
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            client = user_profile.client
        except UserProfile.DoesNotExist:
            client = None

        # Prepare per-platform data sources
        platform_models = [
            ('google_ads', GoogleAdsData),
            ('mailchimp', MailchimpData),
            ('linkedin_ads', LinkedInAdsData),
            ('zoho', ZohoData),
        ]
        platform_data = {}
        # Unified totals
        total_campaigns = 0
        total_spend = 0
        total_revenue = 0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0

        for platform, model in platform_models:
            qs = model.objects.filter(client=client) if client else model.objects.all()
            # Each record is a JSON blob, may contain multiple campaigns
            campaigns = []
            for record in qs.order_by('-fetched_at'):
                data = record.data
                if isinstance(data, list):
                    campaigns.extend(data)
                elif isinstance(data, dict):
                    campaigns.append(data)
            # Aggregate metrics for this platform
            platform_campaigns = len(campaigns)
            spend = sum(float(c.get('spend', 0) or 0) for c in campaigns)
            revenue = sum(float(c.get('revenue', 0) or 0) for c in campaigns)
            impressions = sum(int(c.get('impressions', 0) or 0) for c in campaigns)
            clicks = sum(int(c.get('clicks', 0) or 0) for c in campaigns)
            conversions = sum(int(c.get('conversions', 0) or 0) for c in campaigns)
            # Calculate KPIs
            roas = revenue / spend if spend > 0 else 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
            cpa = spend / conversions if conversions > 0 else 0
            # Store per-platform
            platform_data[platform] = {
                'count': platform_campaigns,
                'spend': spend,
                'revenue': revenue,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'roas': roas,
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'cpa': cpa,
            }
            # Add to unified totals
            total_campaigns += platform_campaigns
            total_spend += spend
            total_revenue += revenue
            total_impressions += impressions
            total_clicks += clicks
            total_conversions += conversions

        # Unified KPIs
        roas = total_revenue / total_spend if total_spend > 0 else 0
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpa = total_spend / total_conversions if total_conversions > 0 else 0

        context = {
            'platform_data': platform_data,
            'total_campaigns': total_campaigns,
            'total_spend': total_spend,
            'total_revenue': total_revenue,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'roas': roas,
            'ctr': ctr,
            'conversion_rate': conversion_rate,
            'cpa': cpa,
            'client': client,
        }
        return render(request, 'dashboard/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        messages.error(request, "An error occurred while loading the dashboard. Please try refreshing the page.")
        return render(request, 'dashboard/dashboard.html', {
            'error': True,
            'error_message': "Unable to load dashboard data. Please contact support if this persists."
        })

@login_required
def campaign_detail(request, campaign_id):
    """Campaign detail view."""
    try:
        campaign = get_object_or_404(Campaign, id=campaign_id)
        
        # Check if user has access to this campaign
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.client and campaign.client != user_profile.client:
                messages.error(request, "You don't have permission to view this campaign.")
                return redirect('dashboard')
        except UserProfile.DoesNotExist:
            pass  # Admin users can view all campaigns
        
        # Get campaign reports
        reports = CampaignReport.objects.filter(campaign=campaign).order_by('-generated_at')
        
        # Calculate additional metrics
        ctr = (campaign.clicks / campaign.impressions * 100) if campaign.impressions > 0 else 0
        conversion_rate = (campaign.conversions / campaign.clicks * 100) if campaign.clicks > 0 else 0
        cpa = campaign.budget / campaign.conversions if campaign.conversions > 0 else 0
        
        context = {
            'campaign': campaign,
            'reports': reports,
            'ctr': ctr,
            'conversion_rate': conversion_rate,
            'cpa': cpa,
        }
        
        return render(request, 'dashboard/campaign_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in campaign detail view: {str(e)}")
        messages.error(request, "An error occurred while loading the campaign details.")
        return redirect('dashboard')

@login_required
def report_list(request):
    """Report list view."""
    try:
        # Get user's client
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            client = user_profile.client
        except UserProfile.DoesNotExist:
            client = None
        
        # Get reports
        if client:
            reports = CampaignReport.objects.filter(client=client).order_by('-generated_at')
        else:
            reports = CampaignReport.objects.all().order_by('-generated_at')
        
        context = {
            'reports': reports,
            'client': client,
        }
        
        return render(request, 'dashboard/report_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in report list view: {str(e)}")
        messages.error(request, "An error occurred while loading the reports.")
        return render(request, 'dashboard/report_list.html', {})

def login_view(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('client_portal')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'dashboard/auth/login.html')

def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'dashboard/auth/register.html', {'form': form})

def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def client_portal(request):
    """Client portal view."""
    try:
        # Get user's client
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            client = user_profile.client
        except UserProfile.DoesNotExist:
            messages.error(request, "You don't have access to the client portal.")
            return redirect('dashboard')
        
        # Get client's campaigns and reports
        campaigns = Campaign.objects.filter(client=client)
        reports = CampaignReport.objects.filter(campaign__client=client).order_by('-generated_at')
        monthly_summaries = MonthlySummary.objects.filter(client=client).order_by('-month')
        
        # Calculate client KPIs
        total_spend = sum(campaign.budget for campaign in campaigns)
        total_revenue = sum(campaign.revenue for campaign in campaigns)
        roas = total_revenue / total_spend if total_spend > 0 else 0
        
        # Get current month summary
        current_month = datetime.now().replace(day=1).date()
        current_month_summary = monthly_summaries.filter(month=current_month).first()
        
        # Get ML predictions and forecasts
        ml_predictions = MLPrediction.objects.filter(client=client, is_active=True).order_by('-created_at')[:5]
        future_forecasts = FutureForecast.objects.filter(client=client).order_by('forecast_date')[:3]
        
        # Get AI insights
        ai_insights = ml_service.get_ai_insights()
        
        # Platform connection status
        platform_connections = {
            'google_ads': client.google_ads_credentials.exists(),
            'linkedin_ads': client.linkedin_ads_credentials.exists(),
            'mailchimp': client.mailchimp_credentials.exists(),
            'zoho': client.zoho_credentials.exists(),
            'demandbase': client.demandbase_credentials.exists(),
        }
        
        context = {
            'client': client,
            'campaigns': campaigns,
            'reports': reports,
            'monthly_summaries': monthly_summaries,
            'current_month_summary': current_month_summary,
            'total_spend': total_spend,
            'total_revenue': total_revenue,
            'roas': roas,
            'ml_predictions': ml_predictions,
            'future_forecasts': future_forecasts,
            'ai_insights': ai_insights,
            'platform_connections': platform_connections,
        }
        
        return render(request, 'dashboard/auth/client_portal.html', context)
        
    except Exception as e:
        logger.error(f"Error in client portal view: {str(e)}")
        messages.error(request, "An error occurred while loading the client portal.")
        return render(request, 'dashboard/auth/client_portal.html', {})

@login_required
def monthly_summary_detail(request, summary_id):
    """Monthly summary detail view."""
    try:
        summary = get_object_or_404(MonthlySummary, id=summary_id)
        
        # Check if user has access to this summary
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.client != summary.client:
                messages.error(request, "You don't have permission to view this summary.")
                return redirect('client_portal')
        except UserProfile.DoesNotExist:
            messages.error(request, "You don't have access to client summaries.")
            return redirect('dashboard')
        
        context = {
            'summary': summary,
            'client': summary.client,
        }
        
        return render(request, 'dashboard/monthly_summary_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in monthly summary detail view: {str(e)}")
        messages.error(request, "An error occurred while loading the summary.")
        return redirect('client_portal')

@csrf_exempt
@require_http_methods(["POST"])
def ml_insights_api(request):
    """API endpoint for ML insights."""
    try:
        data = json.loads(request.body)
        campaign_id = data.get('campaign_id')
        
        if not campaign_id:
            return JsonResponse({'error': 'campaign_id is required'}, status=400)
        
        campaign = get_object_or_404(Campaign, id=campaign_id)
        
        # Simulate ML insights
        insights = {
            'campaign_id': campaign_id,
            'predicted_ctr': round(campaign.ctr * 1.1, 2),
            'predicted_conversion_rate': round((campaign.conversions / campaign.clicks * 100) * 1.05, 2) if campaign.clicks > 0 else 0,
            'recommended_budget': round(campaign.budget * 1.15, 2),
            'optimization_suggestions': [
                "Consider increasing budget by 15% for better reach",
                "Target audience shows high engagement potential",
                "Ad copy optimization could improve CTR by 10%"
            ],
            'risk_factors': [
                "Seasonal fluctuations may affect performance",
                "Competition intensity is moderate"
            ]
        }
        
        return JsonResponse(insights)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in ML insights API: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('dashboard')
    
    try:
        # Get overall statistics
        total_clients = Client.objects.count()
        total_campaigns = Campaign.objects.count()
        total_reports = CampaignReport.objects.count()
        total_users = User.objects.count()
        
        # Get recent activity
        recent_campaigns = Campaign.objects.order_by('-created_at')[:5]
        recent_reports = CampaignReport.objects.order_by('-generated_at')[:5]
        
        context = {
            'total_clients': total_clients,
            'total_campaigns': total_campaigns,
            'total_reports': total_reports,
            'total_users': total_users,
            'recent_campaigns': recent_campaigns,
            'recent_reports': recent_reports,
        }
        
        return render(request, 'dashboard/admin_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin dashboard view: {str(e)}")
        messages.error(request, "An error occurred while loading the admin dashboard.")
        return render(request, 'dashboard/admin_dashboard.html', {})

@login_required
def ml_predictions_view(request):
    """View for displaying ML predictions and forecasts."""
    try:
        # Get user's client
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            client = user_profile.client
        except UserProfile.DoesNotExist:
            messages.error(request, "You don't have access to ML predictions.")
            return redirect('dashboard')
        
        # Get ML predictions
        campaign_predictions = MLPrediction.objects.filter(
            client=client, 
            prediction_type='campaign',
            is_active=True
        ).order_by('-created_at')
        
        monthly_forecasts = MLPrediction.objects.filter(
            client=client,
            prediction_type='monthly_forecast',
            is_active=True
        ).order_by('-created_at')
        
        # Get future forecasts
        future_forecasts = FutureForecast.objects.filter(client=client).order_by('forecast_date')
        
        # Get AI insights
        ai_insights = ml_service.get_ai_insights()
        
        # Get monthly forecast data
        monthly_forecast_data = ml_service.get_monthly_forecast(6)  # 6 months ahead
        
        context = {
            'client': client,
            'campaign_predictions': campaign_predictions,
            'monthly_forecasts': monthly_forecasts,
            'future_forecasts': future_forecasts,
            'ai_insights': ai_insights,
            'monthly_forecast_data': monthly_forecast_data,
        }
        
        return render(request, 'dashboard/ml_predictions.html', context)
        
    except Exception as e:
        logger.error(f"Error in ML predictions view: {str(e)}")
        messages.error(request, "An error occurred while loading ML predictions.")
        return render(request, 'dashboard/ml_predictions.html', {})

@login_required
def campaign_prediction_detail(request, prediction_id):
    """Detailed view for a specific ML prediction."""
    try:
        prediction = get_object_or_404(MLPrediction, id=prediction_id)
        
        # Check if user has access
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.client and prediction.client != user_profile.client:
                messages.error(request, "You don't have permission to view this prediction.")
                return redirect('ml_predictions')
        except UserProfile.DoesNotExist:
            pass
        
        context = {
            'prediction': prediction,
            'client': prediction.client,
        }
        
        return render(request, 'dashboard/campaign_prediction_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in campaign prediction detail view: {str(e)}")
        messages.error(request, "An error occurred while loading the prediction details.")
        return redirect('ml_predictions')

@csrf_exempt
@require_http_methods(["POST"])
def generate_ml_prediction(request):
    """API endpoint to generate new ML predictions."""
    try:
        data = json.loads(request.body)
        client_id = data.get('client_id')
        campaign_id = data.get('campaign_id')
        prediction_type = data.get('prediction_type', 'campaign')
        
        client = get_object_or_404(Client, id=client_id)
        campaign = None
        if campaign_id:
            campaign = get_object_or_404(Campaign, id=campaign_id)
        
        # Generate prediction using ML service
        if campaign:
            campaign_data = {
                'platform': campaign.platform,
                'spend': float(campaign.spend),
                'impressions': campaign.impressions,
                'clicks': campaign.clicks,
                'conversions': campaign.conversions,
            }
            prediction_result = ml_service.predict_campaign_performance(campaign_data)
        else:
            prediction_result = ml_service.get_monthly_forecast(3)
        
        # Save prediction to database
        prediction = MLPrediction.objects.create(
            client=client,
            campaign=campaign,
            prediction_type=prediction_type,
            predicted_metrics=prediction_result.get('predictions', {}),
            confidence_score=0.85,  # Default confidence
            insights=prediction_result.get('insights', []),
            recommendations=prediction_result.get('recommendations', []),
        )
        
        return JsonResponse({
            'success': True,
            'prediction_id': prediction.id,
            'message': 'ML prediction generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error generating ML prediction: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def unified_data_list(request):
    """View for listing uploaded unified data"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'profile') or not request.user.profile.client:
        messages.error(request, "You don't have permission to view this data.")
        return redirect('dashboard')
    
    client = request.user.profile.client
    unified_data_list = UnifiedClientData.objects.filter(client=client).order_by('-uploaded_at')
    return render(request, 'dashboard/unified_data_list.html', {
        'client': client,
        'unified_data_list': unified_data_list,
    })

def generate_prediction(request, data_id):
    """View for generating predictions from unified data"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'profile') or not request.user.profile.client:
        messages.error(request, "You don't have permission to generate predictions.")
        return redirect('dashboard')
    
    try:
        unified_data = UnifiedClientData.objects.get(id=data_id, client=request.user.profile.client)
    except UnifiedClientData.DoesNotExist:
        messages.error(request, "Data not found.")
        return redirect('unified_data_list')
    
    if request.method == 'POST':
        prediction_type = request.POST.get('prediction_type', 'monthly_forecast')
        
        try:
            # Generate prediction
            prediction = generate_client_prediction(unified_data, prediction_type)
            messages.success(request, f"{prediction_type.replace('_', ' ').title()} generated successfully!")
            return redirect('prediction_detail', prediction_id=prediction.id)
        except Exception as e:
            messages.error(request, f"Error generating prediction: {str(e)}")
    
    return render(request, 'dashboard/generate_prediction.html', {
        'unified_data': unified_data
    })

def prediction_detail(request, prediction_id):
    """View for displaying prediction details"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        prediction = ClientPrediction.objects.get(
            id=prediction_id, 
            client=request.user.profile.client
        )
    except ClientPrediction.DoesNotExist:
        messages.error(request, "Prediction not found.")
        return redirect('unified_data_list')
    
    return render(request, 'dashboard/prediction_detail.html', {
        'prediction': prediction
    })

def download_excel_dashboard(request, data_id):
    """View for downloading Excel dashboard"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        unified_data = UnifiedClientData.objects.get(
            id=data_id, 
            client=request.user.profile.client
        )
    except UnifiedClientData.DoesNotExist:
        messages.error(request, "Data not found.")
        return redirect('unified_data_list')
    
    if not unified_data.excel_dashboard_path:
        messages.error(request, "Excel dashboard not available for this data.")
        return redirect('unified_data_list')
    
    # Check if file exists
    if not os.path.exists(unified_data.excel_dashboard_path):
        messages.error(request, "Excel dashboard file not found.")
        return redirect('unified_data_list')
    
    # Generate filename for download
    filename = f"Targetorate_Dashboard_{unified_data.client.company.replace(' ', '_')}_{unified_data.uploaded_at.strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Return file as download
    with open(unified_data.excel_dashboard_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

def process_unified_data(unified_data):
    """Process uploaded unified data"""
    unified_data.status = 'processing'
    unified_data.processing_started_at = datetime.now()
    unified_data.save()
    
    try:
        # Read the uploaded file
        file_path = unified_data.file.path
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Basic data processing
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        # Calculate summary statistics
        summary = {
            'total_records': len(df),
            'date_range_start': df['Date'].min().strftime('%Y-%m-%d'),
            'date_range_end': df['Date'].max().strftime('%Y-%m-%d'),
            'platforms_included': df['Platform'].unique().tolist(),
            'total_impressions': int(df['Impressions'].sum()),
            'total_clicks': int(df['Clicks'].sum()),
            'total_spend': float(df['Spend'].sum()),
            'total_revenue': float(df['Revenue'].sum()),
            'avg_ctr': float((df['Clicks'] / df['Impressions']).mean() * 100),
            'avg_cpc': float((df['Spend'] / df['Clicks']).mean()),
            'overall_roas': float(df['Revenue'].sum() / df['Spend'].sum()) if df['Spend'].sum() > 0 else 0
        }
        
        # Generate insights
        insights = generate_insights(df)
        recommendations = generate_recommendations(df)
        
        # Update the model
        unified_data.status = 'analyzed'
        unified_data.total_records = summary['total_records']
        unified_data.date_range_start = df['Date'].min().date()
        unified_data.date_range_end = df['Date'].max().date()
        unified_data.platforms_included = summary['platforms_included']
        unified_data.data_summary = summary
        unified_data.insights = insights
        unified_data.recommendations = recommendations
        unified_data.processing_completed_at = datetime.now()
        unified_data.save()
        
        # Generate Excel dashboard
        try:
            excel_generator = ExcelDashboardGenerator()
            
            # Prepare data for Excel dashboard
            excel_data = df.copy()
            excel_data.columns = [col.lower().replace(' ', '_') for col in excel_data.columns]
            
            # Generate predictions for Excel dashboard
            predictions = {}
            try:
                # Generate basic predictions
                monthly_forecast = generate_monthly_forecast(unified_data, df)
                if monthly_forecast:
                    predictions['monthly_forecast'] = {
                        'next_month_revenue': monthly_forecast.get('next_month_revenue', 0),
                        'growth_rate': monthly_forecast.get('growth_rate', 0),
                        'confidence': monthly_forecast.get('confidence', 0)
                    }
            except:
                pass
            
            # Create Excel dashboard
            dashboard_wb = excel_generator.create_dashboard(
                data=excel_data,
                predictions=predictions,
                insights=insights,
                client_name=unified_data.client.company
            )
            
            # Save Excel dashboard
            dashboard_filename = f"dashboard_{unified_data.client.company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            dashboard_path = os.path.join('media', 'excel_dashboards', dashboard_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(dashboard_path), exist_ok=True)
            
            dashboard_wb.save(dashboard_path)
            
            # Update unified data with Excel dashboard path
            unified_data.excel_dashboard_path = dashboard_path
            unified_data.save()
            
        except Exception as excel_error:
            logger.error(f"Error generating Excel dashboard: {str(excel_error)}")
            # Don't fail the entire process if Excel generation fails
        
    except Exception as e:
        unified_data.status = 'failed'
        unified_data.error_message = str(e)
        unified_data.processing_completed_at = datetime.now()
        unified_data.save()
        raise e

def generate_insights(df):
    """Generate AI insights from the data"""
    insights = []
    
    # Platform performance analysis
    platform_performance = df.groupby('Platform').agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    platform_performance['CTR'] = (platform_performance['Clicks'] / platform_performance['Impressions']) * 100
    platform_performance['ROAS'] = platform_performance['Revenue'] / platform_performance['Spend']
    
    best_platform = platform_performance.loc[platform_performance['ROAS'].idxmax()]
    worst_platform = platform_performance.loc[platform_performance['ROAS'].idxmin()]
    
    insights.append({
        'type': 'platform_performance',
        'title': f"Best Performing Platform: {best_platform['Platform']}",
        'description': f"{best_platform['Platform']} has the highest ROAS at {best_platform['ROAS']:.2f}x",
        'priority': 'high'
    })
    
    # Trend analysis
    daily_performance = df.groupby('Date').agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    daily_performance['CTR'] = (daily_performance['Clicks'] / daily_performance['Impressions']) * 100
    
    # Check for trends
    if len(daily_performance) > 7:
        recent_ctr = daily_performance.tail(7)['CTR'].mean()
        overall_ctr = daily_performance['CTR'].mean()
        
        if recent_ctr > overall_ctr * 1.1:
            insights.append({
                'type': 'trend',
                'title': "Improving Click-Through Rate",
                'description': "Recent CTR is 10% higher than average, indicating improving performance",
                'priority': 'medium'
            })
    
    return insights

def generate_recommendations(df):
    """Generate recommendations based on data analysis"""
    recommendations = []
    
    # Budget optimization
    platform_spend = df.groupby('Platform')['Spend'].sum()
    platform_roas = df.groupby('Platform').apply(
        lambda x: x['Revenue'].sum() / x['Spend'].sum() if x['Spend'].sum() > 0 else 0
    )
    
    best_roas_platform = platform_roas.idxmax()
    worst_roas_platform = platform_roas.idxmin()
    
    recommendations.append({
        'type': 'budget_optimization',
        'title': f"Reallocate Budget to {best_roas_platform}",
        'description': f"Consider increasing budget for {best_roas_platform} which has the highest ROAS",
        'action': f"Move 20% of budget from {worst_roas_platform} to {best_roas_platform}"
    })
    
    # Performance optimization
    low_ctr_campaigns = df[df['Clicks'] / df['Impressions'] < 0.01]  # CTR < 1%
    if len(low_ctr_campaigns) > 0:
        recommendations.append({
            'type': 'performance_optimization',
            'title': "Optimize Low-Performing Campaigns",
            'description': f"{len(low_ctr_campaigns)} campaigns have CTR below 1%",
            'action': "Review ad copy, targeting, and keywords for these campaigns"
        })
    
    return recommendations

def generate_client_prediction(unified_data, prediction_type):
    """Generate predictions based on unified data"""
    # Read the processed data
    df = pd.read_csv(unified_data.file.path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Generate predictions based on type
    if prediction_type == 'monthly_forecast':
        return generate_monthly_forecast(unified_data, df)
    elif prediction_type == 'campaign_performance':
        return generate_campaign_performance_prediction(unified_data, df)
    elif prediction_type == 'revenue_prediction':
        return generate_revenue_prediction(unified_data, df)
    else:
        return generate_optimization_prediction(unified_data, df)

def generate_monthly_forecast(unified_data, df):
    """Generate monthly forecast"""
    # Simple forecasting using historical averages
    monthly_data = df.groupby(df['Date'].dt.to_period('M')).agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    # Calculate growth rates
    if len(monthly_data) > 1:
        revenue_growth = (monthly_data['Revenue'].iloc[-1] - monthly_data['Revenue'].iloc[-2]) / monthly_data['Revenue'].iloc[-2]
        spend_growth = (monthly_data['Spend'].iloc[-1] - monthly_data['Spend'].iloc[-2]) / monthly_data['Spend'].iloc[-2]
    else:
        revenue_growth = 0.05  # Default 5% growth
        spend_growth = 0.03    # Default 3% growth
    
    # Predict next month
    last_month = monthly_data.iloc[-1]
    next_month_revenue = last_month['Revenue'] * (1 + revenue_growth)
    next_month_spend = last_month['Spend'] * (1 + spend_growth)
    next_month_impressions = last_month['Impressions'] * 1.02  # 2% growth
    next_month_clicks = last_month['Clicks'] * 1.02
    
    predicted_metrics = {
        'predicted_impressions': int(next_month_impressions),
        'predicted_clicks': int(next_month_clicks),
        'predicted_spend': float(next_month_spend),
        'predicted_revenue': float(next_month_revenue),
        'predicted_ctr': float((next_month_clicks / next_month_impressions) * 100),
        'predicted_roi': float(next_month_revenue / next_month_spend)
    }
    
    # Create prediction
    prediction = ClientPrediction.objects.create(
        client=unified_data.client,
        unified_data=unified_data,
        prediction_type='monthly_forecast',
        target_date=(datetime.now() + timedelta(days=30)).date(),
        predicted_metrics=predicted_metrics,
        confidence_score=0.75,
        insights=unified_data.insights,
        recommendations=unified_data.recommendations
    )
    
    return prediction

def generate_campaign_performance_prediction(unified_data, df):
    """Generate campaign performance prediction"""
    # Analyze campaign performance trends
    campaign_performance = df.groupby('Campaign').agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    campaign_performance['CTR'] = (campaign_performance['Clicks'] / campaign_performance['Impressions']) * 100
    campaign_performance['ROAS'] = campaign_performance['Revenue'] / campaign_performance['Spend']
    
    # Predict performance for top campaigns
    top_campaigns = campaign_performance.nlargest(5, 'Revenue')
    
    predicted_metrics = {
        'top_campaigns': top_campaigns.to_dict('records'),
        'avg_campaign_ctr': float(campaign_performance['CTR'].mean()),
        'avg_campaign_roas': float(campaign_performance['ROAS'].mean()),
        'total_campaigns': len(campaign_performance)
    }
    
    prediction = ClientPrediction.objects.create(
        client=unified_data.client,
        unified_data=unified_data,
        prediction_type='campaign_performance',
        predicted_metrics=predicted_metrics,
        confidence_score=0.80,
        insights=unified_data.insights,
        recommendations=unified_data.recommendations
    )
    
    return prediction

def generate_revenue_prediction(unified_data, df):
    """Generate revenue prediction"""
    # Analyze revenue trends
    daily_revenue = df.groupby('Date')['Revenue'].sum().reset_index()
    
    # Calculate revenue growth rate
    if len(daily_revenue) > 7:
        recent_avg = daily_revenue.tail(7)['Revenue'].mean()
        overall_avg = daily_revenue['Revenue'].mean()
        growth_rate = (recent_avg - overall_avg) / overall_avg
    else:
        growth_rate = 0.05  # Default 5% growth
    
    # Predict future revenue
    current_daily_revenue = daily_revenue['Revenue'].iloc[-1]
    predicted_daily_revenue = current_daily_revenue * (1 + growth_rate)
    predicted_monthly_revenue = predicted_daily_revenue * 30
    
    predicted_metrics = {
        'current_daily_revenue': float(current_daily_revenue),
        'predicted_daily_revenue': float(predicted_daily_revenue),
        'predicted_monthly_revenue': float(predicted_monthly_revenue),
        'growth_rate': float(growth_rate * 100),
        'confidence_interval': f"±{abs(growth_rate * 10):.1f}%"
    }
    
    prediction = ClientPrediction.objects.create(
        client=unified_data.client,
        unified_data=unified_data,
        prediction_type='revenue_prediction',
        predicted_metrics=predicted_metrics,
        confidence_score=0.70,
        insights=unified_data.insights,
        recommendations=unified_data.recommendations
    )
    
    return prediction

def generate_optimization_prediction(unified_data, df):
    """Generate optimization recommendations"""
    # Analyze performance gaps
    platform_performance = df.groupby('Platform').agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    platform_performance['CTR'] = (platform_performance['Clicks'] / platform_performance['Impressions']) * 100
    platform_performance['ROAS'] = platform_performance['Revenue'] / platform_performance['Spend']
    
    # Identify optimization opportunities
    optimization_opportunities = []
    
    for _, platform in platform_performance.iterrows():
        if platform['CTR'] < 2.0:  # Low CTR
            optimization_opportunities.append({
                'platform': platform['Platform'],
                'issue': 'Low CTR',
                'current_value': f"{platform['CTR']:.2f}%",
                'recommendation': 'Optimize ad copy and targeting'
            })
        
        if platform['ROAS'] < 2.0:  # Low ROAS
            optimization_opportunities.append({
                'platform': platform['Platform'],
                'issue': 'Low ROAS',
                'current_value': f"{platform['ROAS']:.2f}x",
                'recommendation': 'Review bidding strategy and audience targeting'
            })
    
    predicted_metrics = {
        'optimization_opportunities': optimization_opportunities,
        'total_platforms': len(platform_performance),
        'platforms_needing_optimization': len(optimization_opportunities),
        'potential_improvement': '15-25%'
    }
    
    prediction = ClientPrediction.objects.create(
        client=unified_data.client,
        unified_data=unified_data,
        prediction_type='optimization',
        predicted_metrics=predicted_metrics,
        confidence_score=0.85,
        insights=unified_data.insights,
        recommendations=unified_data.recommendations
    )
    
    return prediction

@login_required
def connect_google_ads(request):
    client = request.user.profile.client
    if request.method == 'POST':
        form = GoogleAdsCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            # Import Google Ads data after connecting
            df = fetch_google_ads_data()
            from .models import GoogleAdsData
            GoogleAdsData.objects.create(client=client, data=df.to_dict(orient='records'))
            messages.success(request, 'Google Ads account connected and data imported successfully!')
            return redirect('client_portal')
    else:
        form = GoogleAdsCredentialForm()
    return render(request, 'dashboard/connect_google_ads.html', {'form': form})

@login_required
def connect_linkedin_ads(request):
    client = request.user.profile.client
    if request.method == 'POST':
        form = LinkedInAdsCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            # Import LinkedIn Ads data after connecting
            df = fetch_linkedin_ads_data()
            from .models import LinkedInAdsData
            LinkedInAdsData.objects.create(client=client, data=df.to_dict(orient='records'))
            messages.success(request, 'LinkedIn Ads account connected and data imported successfully!')
            return redirect('client_portal')
    else:
        form = LinkedInAdsCredentialForm()
    return render(request, 'dashboard/connect_linkedin_ads.html', {'form': form})

@login_required
def connect_mailchimp(request):
    client = request.user.profile.client
    if request.method == 'POST':
        form = MailchimpCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            # Import Mailchimp data after connecting
            df = fetch_mailchimp_data()
            # Save each row as a MailchimpData record (or as a list)
            from .models import MailchimpData
            MailchimpData.objects.create(client=client, data=df.to_dict(orient='records'))
            messages.success(request, 'Mailchimp account connected and data imported successfully!')
            return redirect('client_portal')
    else:
        form = MailchimpCredentialForm()
    return render(request, 'dashboard/connect_mailchimp.html', {'form': form})

@login_required
def connect_zoho(request):
    client = request.user.profile.client
    if request.method == 'POST':
        form = ZohoCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            # Import Zoho data after connecting
            df = fetch_zoho_data()
            from .models import ZohoData
            ZohoData.objects.create(client=client, data=df.to_dict(orient='records'))
            messages.success(request, 'Zoho account connected and data imported successfully!')
            return redirect('client_portal')
    else:
        form = ZohoCredentialForm()
    return render(request, 'dashboard/connect_zoho.html', {'form': form})

@login_required
def connect_demandbase(request):
    client = request.user.profile.client
    if request.method == 'POST':
        # Simulate a credential form for Demandbase (if needed)
        # If not needed, just import data directly
        # For now, just import data directly
        df = fetch_demandbase_data()
        from .models import DemandbaseCredential, DemandbaseData
        # Create a dummy credential if not exists
        if not client.demandbase_credentials.exists():
            DemandbaseCredential.objects.create(client=client, api_key='dummy')
        # Save data
        DemandbaseData.objects.create(client=client, data=df.to_dict(orient='records'))
        messages.success(request, 'Demandbase connected and data imported successfully!')
        return redirect('client_portal')
    return render(request, 'dashboard/connect_demandbase.html')

@login_required
def unified_insights_view(request):
    """Unified data and insights page for all platforms."""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        client = user_profile.client
    except UserProfile.DoesNotExist:
        client = None

    platform_models = [
        GoogleAdsData,
        MailchimpData,
        LinkedInAdsData,
        ZohoData,
    ]
    unified_campaigns = []
    for model in platform_models:
        qs = model.objects.filter(client=client) if client else model.objects.all()
        for record in qs.order_by('-fetched_at'):
            data = record.data
            if isinstance(data, list):
                unified_campaigns.extend(data)
            elif isinstance(data, dict):
                unified_campaigns.append(data)
    # Calculate unified KPIs
    total_campaigns = len(unified_campaigns)
    total_spend = sum(float(c.get('spend', 0) or 0) for c in unified_campaigns)
    total_revenue = sum(float(c.get('revenue', 0) or 0) for c in unified_campaigns)
    total_impressions = sum(int(c.get('impressions', 0) or 0) for c in unified_campaigns)
    total_clicks = sum(int(c.get('clicks', 0) or 0) for c in unified_campaigns)
    total_conversions = sum(int(c.get('conversions', 0) or 0) for c in unified_campaigns)
    roas = total_revenue / total_spend if total_spend > 0 else 0
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    cpa = total_spend / total_conversions if total_conversions > 0 else 0
    # Example insights (expand later)
    insights = []
    if roas < 1:
        insights.append("ROAS is below 1. Review campaign efficiency.")
    if ctr < 1:
        insights.append("CTR is low. Consider improving ad creatives.")
    context = {
        'unified_campaigns': unified_campaigns,
        'total_campaigns': total_campaigns,
        'total_spend': total_spend,
        'total_revenue': total_revenue,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_conversions': total_conversions,
        'roas': roas,
        'ctr': ctr,
        'conversion_rate': conversion_rate,
        'cpa': cpa,
        'insights': insights,
        'client': client,
    }
    return render(request, 'dashboard/unified_insights.html', context)

@login_required
def monthly_analysis_view(request):
    user_profile = getattr(request.user, 'profile', None)
    client = getattr(user_profile, 'client', None)
    if not client:
        messages.error(request, 'You do not have access to monthly analysis.')
        return redirect('dashboard')
    summaries = MonthlySummary.objects.filter(client=client).order_by('-month')
    prediction_message = None
    if request.method == 'POST' and 'predict_next' in request.POST:
        # Placeholder: trigger prediction for next month
        # In real use, call your ML prediction logic here
        prediction_message = 'Prediction for next month has been generated (simulated).'
    context = {
        'summaries': summaries,
        'client': client,
        'show_predict_button': True,
        'prediction_message': prediction_message,
    }
    return render(request, 'dashboard/monthly_analysis.html', context)

@login_required
def monthly_predictions_view(request, summary_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        client = user_profile.client
    except UserProfile.DoesNotExist:
        client = None
    summary = get_object_or_404(MonthlySummary, id=summary_id, client=client)
    # Get predictions for this month (by date)
    predictions = ClientPrediction.objects.filter(client=client, prediction_type='monthly_forecast', target_date=summary.month)
    context = {
        'summary': summary,
        'predictions': predictions,
        'client': client,
    }
    return render(request, 'dashboard/monthly_predictions.html', context)

@login_required
def download_monthly_predictions(request, summary_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        client = user_profile.client
    except UserProfile.DoesNotExist:
        client = None
    summary = get_object_or_404(MonthlySummary, id=summary_id, client=client)
    predictions = ClientPrediction.objects.filter(client=client, prediction_type='monthly_forecast', target_date=summary.month)
    # Prepare data for Excel
    rows = []
    for p in predictions:
        row = {
            'Prediction Type': p.prediction_type,
            'Target Date': p.target_date,
            'Predicted Metrics': str(p.predicted_metrics),
            'Confidence Score': p.confidence_score,
            'Insights': '; '.join(p.insights) if p.insights else '',
            'Recommendations': '; '.join(p.recommendations) if p.recommendations else '',
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Predictions')
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=monthly_predictions_{summary.month.strftime('%Y_%m')}.xlsx'
    return response

@login_required
def google_ads_analysis(request):
    client = request.user.profile.client
    from .models import GoogleAdsData
    data_obj = GoogleAdsData.objects.filter(client=client).order_by('-fetched_at').first()
    campaigns = data_obj.data if data_obj else []
    # Calculate KPIs
    total_impressions = sum(c.get('impressions', 0) for c in campaigns)
    total_clicks = sum(c.get('clicks', 0) for c in campaigns)
    total_spend = sum(float(c.get('spend', 0)) for c in campaigns)
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    context = {
        'campaigns': campaigns,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_spend': total_spend,
        'ctr': ctr,
        'client': client,
    }
    return render(request, 'dashboard/google_ads_analysis.html', context)

@login_required
def linkedin_ads_analysis(request):
    client = request.user.profile.client
    from .models import LinkedInAdsData
    data_obj = LinkedInAdsData.objects.filter(client=client).order_by('-fetched_at').first()
    campaigns = data_obj.data if data_obj else []
    total_spend = sum(float(c.get('spend', 0)) for c in campaigns)
    total_conversions = sum(c.get('conversions', 0) for c in campaigns)
    avg_cpl = (total_spend / total_conversions) if total_conversions > 0 else 0
    context = {
        'campaigns': campaigns,
        'total_spend': total_spend,
        'total_conversions': total_conversions,
        'avg_cpl': avg_cpl,
        'client': client,
    }
    return render(request, 'dashboard/linkedin_ads_analysis.html', context)

@login_required
def mailchimp_analysis(request):
    client = request.user.profile.client
    from .models import MailchimpData
    data_obj = MailchimpData.objects.filter(client=client).order_by('-fetched_at').first()
    campaigns = data_obj.data if data_obj else []
    total_opens = sum(c.get('open_rate', 0) for c in campaigns)
    total_clicks = sum(c.get('click_rate', 0) for c in campaigns)
    context = {
        'campaigns': campaigns,
        'total_opens': total_opens,
        'total_clicks': total_clicks,
        'client': client,
    }
    return render(request, 'dashboard/mailchimp_analysis.html', context)

@login_required
def zoho_analysis(request):
    client = request.user.profile.client
    from .models import ZohoData
    data_obj = ZohoData.objects.filter(client=client).order_by('-fetched_at').first()
    campaigns = data_obj.data if data_obj else []
    total_leads = sum(c.get('leads', 0) for c in campaigns)
    total_deals = sum(c.get('deals', 0) for c in campaigns)
    context = {
        'campaigns': campaigns,
        'total_leads': total_leads,
        'total_deals': total_deals,
        'client': client,
    }
    return render(request, 'dashboard/zoho_analysis.html', context)

@login_required
def demandbase_analysis(request):
    client = request.user.profile.client
    from .models import DemandbaseData
    data_obj = DemandbaseData.objects.filter(client=client).order_by('-fetched_at').first()
    campaigns = data_obj.data if data_obj else []
    avg_intent_score = (sum(c.get('intent_score', 0) for c in campaigns) / len(campaigns)) if campaigns else 0
    context = {
        'campaigns': campaigns,
        'avg_intent_score': avg_intent_score,
        'client': client,
    }
    return render(request, 'dashboard/demandbase_analysis.html', context)

@login_required
def unified_analytics(request):
    client = request.user.profile.client
    from .models import GoogleAdsData, MailchimpData, LinkedInAdsData, ZohoData, DemandbaseData
    # Fetch latest data for each platform
    google_ads = GoogleAdsData.objects.filter(client=client).order_by('-fetched_at').first()
    mailchimp = MailchimpData.objects.filter(client=client).order_by('-fetched_at').first()
    linkedin = LinkedInAdsData.objects.filter(client=client).order_by('-fetched_at').first()
    zoho = ZohoData.objects.filter(client=client).order_by('-fetched_at').first()
    demandbase = DemandbaseData.objects.filter(client=client).order_by('-fetched_at').first()
    # Convert to DataFrames
    dfs = []
    if google_ads and google_ads.data:
        df = pd.DataFrame(google_ads.data)
        df['platform'] = 'Google Ads'
        dfs.append(df)
    if mailchimp and mailchimp.data:
        df = pd.DataFrame(mailchimp.data)
        df['platform'] = 'Mailchimp'
        dfs.append(df)
    if linkedin and linkedin.data:
        df = pd.DataFrame(linkedin.data)
        df['platform'] = 'LinkedIn Ads'
        dfs.append(df)
    if zoho and zoho.data:
        df = pd.DataFrame(zoho.data)
        df['platform'] = 'Zoho'
        dfs.append(df)
    if demandbase and demandbase.data:
        df = pd.DataFrame(demandbase.data)
        df['platform'] = 'Demandbase'
        dfs.append(df)
    if dfs:
        unified_df = pd.concat(dfs, ignore_index=True)
    else:
        unified_df = pd.DataFrame()
    # Compute unified KPIs
    total_spend = unified_df['spend'].sum() if 'spend' in unified_df else 0
    total_clicks = unified_df['clicks'].sum() if 'clicks' in unified_df else 0
    total_impressions = unified_df['impressions'].sum() if 'impressions' in unified_df else 0
    total_conversions = unified_df['conversions'].sum() if 'conversions' in unified_df else 0
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpl = (total_spend / total_conversions) if total_conversions > 0 else 0
    # Example insights
    insights = []
    if avg_ctr < 1:
        insights.append('Overall CTR is low. Consider improving ad creatives.')
    if avg_cpl > 50:
        insights.append('Cost per lead is high. Review targeting and bidding strategies.')
    if total_spend > 0 and total_conversions == 0:
        insights.append('No conversions despite spend. Check campaign setup.')
    # Prepare data for charts (group by platform)
    spend_by_platform = unified_df.groupby('platform')['spend'].sum().to_dict() if 'spend' in unified_df else {}
    conversions_by_platform = unified_df.groupby('platform')['conversions'].sum().to_dict() if 'conversions' in unified_df else {}
    spend_labels = json.dumps(list(spend_by_platform.keys()))
    spend_values = json.dumps(list(spend_by_platform.values()))
    conversions_labels = json.dumps(list(conversions_by_platform.keys()))
    conversions_values = json.dumps(list(conversions_by_platform.values()))
    context = {
        'unified_df': unified_df.to_dict(orient='records'),
        'total_spend': total_spend,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'total_conversions': total_conversions,
        'avg_ctr': avg_ctr,
        'avg_cpl': avg_cpl,
        'insights': insights,
        'spend_by_platform': spend_by_platform,
        'conversions_by_platform': conversions_by_platform,
        'spend_labels': spend_labels,
        'spend_values': spend_values,
        'conversions_labels': conversions_labels,
        'conversions_values': conversions_values,
        'client': client,
    }
    return render(request, 'dashboard/unified_analytics.html', context)

@login_required
def download_unified_analytics(request):
    client = request.user.profile.client
    from .models import GoogleAdsData, MailchimpData, LinkedInAdsData, ZohoData, DemandbaseData
    google_ads = GoogleAdsData.objects.filter(client=client).order_by('-fetched_at').first()
    mailchimp = MailchimpData.objects.filter(client=client).order_by('-fetched_at').first()
    linkedin = LinkedInAdsData.objects.filter(client=client).order_by('-fetched_at').first()
    zoho = ZohoData.objects.filter(client=client).order_by('-fetched_at').first()
    demandbase = DemandbaseData.objects.filter(client=client).order_by('-fetched_at').first()
    dfs = []
    if google_ads and google_ads.data:
        df = pd.DataFrame(google_ads.data)
        df['platform'] = 'Google Ads'
        dfs.append(df)
    if mailchimp and mailchimp.data:
        df = pd.DataFrame(mailchimp.data)
        df['platform'] = 'Mailchimp'
        dfs.append(df)
    if linkedin and linkedin.data:
        df = pd.DataFrame(linkedin.data)
        df['platform'] = 'LinkedIn Ads'
        dfs.append(df)
    if zoho and zoho.data:
        df = pd.DataFrame(zoho.data)
        df['platform'] = 'Zoho'
        dfs.append(df)
    if demandbase and demandbase.data:
        df = pd.DataFrame(demandbase.data)
        df['platform'] = 'Demandbase'
        dfs.append(df)
    if dfs:
        unified_df = pd.concat(dfs, ignore_index=True)
    else:
        unified_df = pd.DataFrame()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        unified_df.to_excel(writer, index=False, sheet_name='Unified Analytics')
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=unified_analytics.xlsx'
    return response

@login_required
def connect_tools_portal(request):
    context = {
        'google_ads_form': GoogleAdsCredentialForm(),
        'linkedin_ads_form': LinkedInAdsCredentialForm(),
        'mailchimp_form': MailchimpCredentialForm(),
        'zoho_form': ZohoCredentialForm(),
    }
    return render(request, 'dashboard/connect_mailchimp.html', context)

@login_required
@require_POST
def sync_all_data(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = user_profile.client
    results = {}
    try:
        # Check which platforms are connected for this client
        if GoogleAdsCredential.objects.filter(client=client).exists():
            try:
                import_google_ads_data(client)
                results['google_ads'] = 'success'
            except Exception as e:
                results['google_ads'] = f'error: {str(e)}'
        if LinkedInAdsCredential.objects.filter(client=client).exists():
            try:
                import_linkedin_ads_data(client)
                results['linkedin_ads'] = 'success'
            except Exception as e:
                results['linkedin_ads'] = f'error: {str(e)}'
        if MailchimpCredential.objects.filter(client=client).exists():
            try:
                import_mailchimp_data(client)
                results['mailchimp'] = 'success'
            except Exception as e:
                results['mailchimp'] = f'error: {str(e)}'
        if ZohoCredential.objects.filter(client=client).exists():
            try:
                import_zoho_data(client)
                results['zoho'] = 'success'
            except Exception as e:
                results['zoho'] = f'error: {str(e)}'
        if DemandbaseCredential.objects.filter(client=client).exists():
            try:
                import_demandbase_data(client)
                results['demandbase'] = 'success'
            except Exception as e:
                results['demandbase'] = f'error: {str(e)}'
        return JsonResponse({'status': 'ok', 'results': results})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_GET
def dashboard_data_api(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = user_profile.client
    # Replicate the dashboard context logic
    # (Assume you have a function get_dashboard_context(client) that returns the context dict)
    context = get_dashboard_context(client)
    # Remove any non-serializable objects (like QuerySets)
    for k, v in context.items():
        if hasattr(v, 'to_dict'):
            context[k] = v.to_dict()
        elif hasattr(v, 'tolist'):
            context[k] = v.tolist()
    return JsonResponse(context)

@login_required
@require_POST
def connect_google_ads_ajax(request):
    """AJAX endpoint for connecting Google Ads with JSON response."""
    try:
        client = request.user.profile.client
        form = GoogleAdsCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            
            # Import Google Ads data after connecting
            try:
                df = fetch_google_ads_data()
                from .models import GoogleAdsData
                GoogleAdsData.objects.create(client=client, data=df.to_dict(orient='records'))
                return JsonResponse({
                    'status': 'success',
                    'message': 'Google Ads account connected and data imported successfully!',
                    'platform': 'google_ads'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'partial_success',
                    'message': f'Google Ads connected but data import failed: {str(e)}',
                    'platform': 'google_ads'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data. Please check your credentials.',
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }, status=500)

@login_required
@require_POST
def connect_linkedin_ads_ajax(request):
    """AJAX endpoint for connecting LinkedIn Ads with JSON response."""
    try:
        client = request.user.profile.client
        form = LinkedInAdsCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            
            # Import LinkedIn Ads data after connecting
            try:
                df = fetch_linkedin_ads_data()
                from .models import LinkedInAdsData
                LinkedInAdsData.objects.create(client=client, data=df.to_dict(orient='records'))
                return JsonResponse({
                    'status': 'success',
                    'message': 'LinkedIn Ads account connected and data imported successfully!',
                    'platform': 'linkedin_ads'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'partial_success',
                    'message': f'LinkedIn Ads connected but data import failed: {str(e)}',
                    'platform': 'linkedin_ads'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data. Please check your credentials.',
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }, status=500)

@login_required
@require_POST
def connect_mailchimp_ajax(request):
    """AJAX endpoint for connecting Mailchimp with JSON response."""
    try:
        client = request.user.profile.client
        form = MailchimpCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            
            # Import Mailchimp data after connecting
            try:
                df = fetch_mailchimp_data()
                from .models import MailchimpData
                MailchimpData.objects.create(client=client, data=df.to_dict(orient='records'))
                return JsonResponse({
                    'status': 'success',
                    'message': 'Mailchimp account connected and data imported successfully!',
                    'platform': 'mailchimp'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'partial_success',
                    'message': f'Mailchimp connected but data import failed: {str(e)}',
                    'platform': 'mailchimp'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data. Please check your credentials.',
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }, status=500)

@login_required
@require_POST
def connect_zoho_ajax(request):
    """AJAX endpoint for connecting Zoho with JSON response."""
    try:
        client = request.user.profile.client
        form = ZohoCredentialForm(request.POST)
        if form.is_valid():
            cred = form.save(commit=False)
            cred.client = client
            cred.save()
            
            # Import Zoho data after connecting
            try:
                df = fetch_zoho_data()
                from .models import ZohoData
                ZohoData.objects.create(client=client, data=df.to_dict(orient='records'))
                return JsonResponse({
                    'status': 'success',
                    'message': 'Zoho account connected and data imported successfully!',
                    'platform': 'zoho'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'partial_success',
                    'message': f'Zoho connected but data import failed: {str(e)}',
                    'platform': 'zoho'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data. Please check your credentials.',
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }, status=500)

@login_required
@require_POST
def connect_demandbase_ajax(request):
    """AJAX endpoint for connecting Demandbase with JSON response."""
    try:
        client = request.user.profile.client
        
        # Import Demandbase data directly (no credentials needed)
        try:
            df = fetch_demandbase_data()
            from .models import DemandbaseCredential, DemandbaseData
            # Create a dummy credential if not exists
            if not client.demandbase_credentials.exists():
                DemandbaseCredential.objects.create(client=client, api_key='dummy')
            # Save data
            DemandbaseData.objects.create(client=client, data=df.to_dict(orient='records'))
            return JsonResponse({
                'status': 'success',
                'message': 'Demandbase connected and data imported successfully!',
                'platform': 'demandbase'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Demandbase connection failed: {str(e)}'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }, status=500)

@login_required
@require_POST
def disconnect_platform_ajax(request):
    """AJAX endpoint for disconnecting a platform."""
    try:
        client = request.user.profile.client
        platform = request.POST.get('platform')
        
        if platform == 'google_ads':
            from .models import GoogleAdsCredential, GoogleAdsData
            GoogleAdsCredential.objects.filter(client=client).delete()
            GoogleAdsData.objects.filter(client=client).delete()
        elif platform == 'linkedin_ads':
            from .models import LinkedInAdsCredential, LinkedInAdsData
            LinkedInAdsCredential.objects.filter(client=client).delete()
            LinkedInAdsData.objects.filter(client=client).delete()
        elif platform == 'mailchimp':
            from .models import MailchimpCredential, MailchimpData
            MailchimpCredential.objects.filter(client=client).delete()
            MailchimpData.objects.filter(client=client).delete()
        elif platform == 'zoho':
            from .models import ZohoCredential, ZohoData
            ZohoCredential.objects.filter(client=client).delete()
            ZohoData.objects.filter(client=client).delete()
        elif platform == 'demandbase':
            from .models import DemandbaseCredential, DemandbaseData
            DemandbaseCredential.objects.filter(client=client).delete()
            DemandbaseData.objects.filter(client=client).delete()
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid platform specified.'
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{platform.replace("_", " ").title()} disconnected successfully!',
            'platform': platform
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Disconnection failed: {str(e)}'
        }, status=500)

@login_required
@require_GET
def get_connection_status(request):
    """Get connection status for all platforms."""
    try:
        client = request.user.profile.client
        status = {}
        
        from .models import (
            GoogleAdsCredential, LinkedInAdsCredential, MailchimpCredential, 
            ZohoCredential, DemandbaseCredential
        )
        
        status['google_ads'] = GoogleAdsCredential.objects.filter(client=client).exists()
        status['linkedin_ads'] = LinkedInAdsCredential.objects.filter(client=client).exists()
        status['mailchimp'] = MailchimpCredential.objects.filter(client=client).exists()
        status['zoho'] = ZohoCredential.objects.filter(client=client).exists()
        status['demandbase'] = DemandbaseCredential.objects.filter(client=client).exists()
        
        return JsonResponse({
            'status': 'success',
            'connections': status
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to get connection status: {str(e)}'
        }, status=500)

@login_required
def google_oauth_callback(request):
    """Handle Google OAuth callback."""
    try:
        from django.conf import settings
        
        # Verify state parameter
        state = request.GET.get('state')
        stored_state = request.session.get('google_oauth_state')
        
        if not state or not stored_state or state != stored_state:
            messages.error(request, 'Invalid OAuth state parameter')
            return redirect('connect_tools_portal')
        
        # Get authorization code
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'No authorization code received')
            return redirect('connect_tools_portal')
        
        # Exchange code for tokens
        token_data = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI
        }
        
        response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_response = response.json()
        
        if 'error' in token_response:
            messages.error(request, f'Token exchange failed: {token_response.get("error_description", "Unknown error")}')
            return redirect('connect_tools_portal')
        
        # Save credentials to database
        client = request.user.profile.client
        from .models import GoogleAdsCredential
        
        # Create or update credential
        credential, created = GoogleAdsCredential.objects.get_or_create(
            client=client,
            defaults={
                'access_token': token_response['access_token'],
                'refresh_token': token_response.get('refresh_token'),
                'token_expires_at': datetime.now() + timedelta(seconds=token_response.get('expires_in', 3600))
            }
        )
        
        if not created:
            credential.access_token = token_response['access_token']
            credential.refresh_token = token_response.get('refresh_token')
            credential.token_expires_at = datetime.now() + timedelta(seconds=token_response.get('expires_in', 3600))
            credential.save()
        
        # Import Google Ads data
        try:
            df = fetch_google_ads_data()
            from .models import GoogleAdsData
            GoogleAdsData.objects.create(client=client, data=df.to_dict(orient='records'))
            
            messages.success(request, 'Google Ads connected successfully via OAuth!')
            return redirect('connect_tools_portal')
        except Exception as e:
            messages.warning(request, f'Google Ads connected but data import failed: {str(e)}')
            return redirect('connect_tools_portal')
            
    except Exception as e:
        messages.error(request, f'OAuth callback failed: {str(e)}')
        return redirect('connect_tools_portal')

@login_required
def linkedin_oauth_callback(request):
    """Handle LinkedIn OAuth callback."""
    try:
        from django.conf import settings
        
        # Verify state parameter
        state = request.GET.get('state')
        stored_state = request.session.get('linkedin_oauth_state')
        
        if not state or not stored_state or state != stored_state:
            messages.error(request, 'Invalid OAuth state parameter')
            return redirect('connect_tools_portal')
        
        # Get authorization code
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'No authorization code received')
            return redirect('connect_tools_portal')
        
        # Exchange code for tokens
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.LINKEDIN_OAUTH_REDIRECT_URI,
            'client_id': settings.LINKEDIN_OAUTH_CLIENT_ID,
            'client_secret': settings.LINKEDIN_OAUTH_CLIENT_SECRET
        }
        
        response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=token_data)
        token_response = response.json()
        
        if 'error' in token_response:
            messages.error(request, f'Token exchange failed: {token_response.get("error_description", "Unknown error")}')
            return redirect('connect_tools_portal')
        
        # Save credentials to database
        client = request.user.profile.client
        from .models import LinkedInAdsCredential
        
        # Create or update credential
        credential, created = LinkedInAdsCredential.objects.get_or_create(
            client=client,
            defaults={
                'access_token': token_response['access_token'],
                'token_expires_at': datetime.now() + timedelta(seconds=token_response.get('expires_in', 3600))
            }
        )
        
        if not created:
            credential.access_token = token_response['access_token']
            credential.token_expires_at = datetime.now() + timedelta(seconds=token_response.get('expires_in', 3600))
            credential.save()
        
        # Import LinkedIn Ads data
        try:
            df = fetch_linkedin_ads_data()
            from .models import LinkedInAdsData
            LinkedInAdsData.objects.create(client=client, data=df.to_dict(orient='records'))
            
            messages.success(request, 'LinkedIn Ads connected successfully via OAuth!')
            return redirect('connect_tools_portal')
        except Exception as e:
            messages.warning(request, f'LinkedIn Ads connected but data import failed: {str(e)}')
            return redirect('connect_tools_portal')
            
    except Exception as e:
        messages.error(request, f'OAuth callback failed: {str(e)}')
        return redirect('connect_tools_portal')

def refresh_google_token(credential):
    """Refresh Google OAuth token."""
    try:
        from django.conf import settings
        
        refresh_data = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'refresh_token': credential.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post('https://oauth2.googleapis.com/token', data=refresh_data)
        token_response = response.json()
        
        if 'error' in token_response:
            raise Exception(f"Token refresh failed: {token_response.get('error_description', 'Unknown error')}")
        
        # Update credential with new token
        credential.access_token = token_response['access_token']
        credential.token_expires_at = datetime.now() + timedelta(seconds=token_response.get('expires_in', 3600))
        credential.save()
        
        return True
    except Exception as e:
        logger.error(f"Failed to refresh Google token: {str(e)}")
        raise

def refresh_linkedin_token(credential):
    """Refresh LinkedIn OAuth token."""
    try:
        from django.conf import settings
        
        refresh_data = {
            'grant_type': 'refresh_token',
            'refresh_token': credential.refresh_token,
            'client_id': settings.LINKEDIN_OAUTH_CLIENT_ID,
            'client_secret': settings.LINKEDIN_OAUTH_CLIENT_SECRET
        }
        
        response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=refresh_data)
        token_response = response.json()
        
        if 'error' in token_response:
            raise Exception(f"Token refresh failed: {token_response.get('error_description', 'Unknown error')}")
        
        # Update credential with new token
        credential.access_token = token_response['access_token']
        credential.token_expires_at = datetime.now() + timedelta(seconds=token_response.get('expires_in', 3600))
        credential.save()
        
        return True
    except Exception as e:
        logger.error(f"Failed to refresh LinkedIn token: {str(e)}")
        raise
