from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .forms import UserRegistrationForm, LoginForm, ClientForm, UserProfileForm, CampaignFilterForm, UserEditForm
from .models import Client, Campaign, CampaignReport, UserProfile

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to the dashboard.')
            
            # Check if user has a client profile and redirect accordingly
            try:
                profile = user.profile
                if profile.client:
                    return redirect('client_portal')
                else:
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'dashboard/auth/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        # Check if user has a client profile and redirect accordingly
        try:
            profile = request.user.profile
            if profile.client:
                return redirect('client_portal')
            else:
                return redirect('dashboard')
        except UserProfile.DoesNotExist:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Check if user has a client profile and redirect accordingly
                try:
                    profile = user.profile
                    if profile.client:
                        return redirect('client_portal')
                    else:
                        return redirect('dashboard')
                except UserProfile.DoesNotExist:
                    return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'dashboard/auth/login.html', {'form': form})

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'user_form': user_form,
        'form': profile_form,
        'user': request.user,
    }
    return render(request, 'dashboard/auth/profile.html', context)

@login_required
def client_portal_view(request):
    """Client portal view - shows only campaigns for the user's client"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('dashboard')
    
    # Get campaigns for this client
    campaigns = Campaign.objects.filter(client=client)
    
    # Apply filters
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
    
    # Pagination
    paginator = Paginator(campaigns, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate client-level KPIs
    total_campaigns = campaigns.count()
    active_campaigns = campaigns.filter(status='active').count()
    total_spend = campaigns.aggregate(total=Sum('spend'))['total'] or 0
    total_revenue = campaigns.aggregate(total=Sum('revenue'))['total'] or 0
    avg_ctr = campaigns.aggregate(avg=Avg('ctr'))['avg'] or 0
    avg_roi = campaigns.aggregate(avg=Avg('roi'))['avg'] or 0
    
    # Get recent reports
    recent_reports = CampaignReport.objects.filter(
        campaign__client=client
    ).order_by('-generated_at')[:5]
    
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
def client_campaign_detail_view(request, campaign_id):
    """Client-specific campaign detail view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('dashboard')
    
    # Get campaign for this client only
    campaign = get_object_or_404(Campaign, id=campaign_id, client=client)
    
    # Get reports for this campaign
    reports = CampaignReport.objects.filter(campaign=campaign).order_by('-generated_at')
    
    # Get ML insights if available
    ml_insights = get_ml_insights_for_campaign(campaign)
    
    context = {
        'campaign': campaign,
        'reports': reports,
        'ml_insights': ml_insights,
        'client': client,
        'profile': profile,
    }
    return render(request, 'dashboard/auth/client_campaign_detail.html', context)

@login_required
def client_reports_view(request):
    """Client-specific reports view"""
    try:
        profile = request.user.profile
        client = profile.client
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if not client:
        messages.error(request, 'No client associated with your account.')
        return redirect('dashboard')
    
    # Get reports for this client's campaigns
    reports = CampaignReport.objects.filter(
        campaign__client=client
    ).order_by('-generated_at')
    
    # Apply filters
    report_type = request.GET.get('report_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    if date_from:
        reports = reports.filter(generated_at__date__gte=date_from)
    if date_to:
        reports = reports.filter(generated_at__date__lte=date_to)
    
    # Calculate summary statistics
    total_spend = reports.aggregate(total=Sum('total_spend'))['total'] or 0
    total_revenue = reports.aggregate(total=Sum('total_revenue'))['total'] or 0
    avg_roi = reports.aggregate(avg=Avg('roi'))['avg'] or 0
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'client': client,
        'profile': profile,
        'report_types': CampaignReport.REPORT_TYPE_CHOICES,
        'total_spend': total_spend,
        'total_revenue': total_revenue,
        'avg_roi': avg_roi,
    }
    return render(request, 'dashboard/auth/client_reports.html', context)

def get_ml_insights_for_campaign(campaign):
    """Get ML insights for a specific campaign"""
    try:
        # Import ML prediction function
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        from ml.predict import get_predictions
        
        # Prepare campaign data for prediction
        campaign_data = {
            'impressions': campaign.impressions,
            'clicks': campaign.clicks,
            'spend': float(campaign.spend),
            'platform': campaign.platform,
        }
        
        predictions = get_predictions(campaign_data)
        return predictions
    except Exception as e:
        return {
            'ml_available': False,
            'error': str(e)
        }

# Admin views for managing clients and users
@login_required
def admin_clients_view(request):
    """Admin view for managing clients"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    clients = Client.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client created successfully!')
            return redirect('admin_clients')
    else:
        form = ClientForm()
    
    context = {
        'clients': clients,
        'form': form,
    }
    return render(request, 'dashboard/admin/clients.html', context)

@login_required
def admin_users_view(request):
    """Admin view for managing users"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    users = User.objects.select_related('profile').all().order_by('username')
    
    context = {
        'users': users,
    }
    return render(request, 'dashboard/admin/users.html', context) 