from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .forms import (
    UserRegistrationForm, LoginForm, UserProfileForm,
    CampaignFilterForm, UserEditForm
)
from .models import Client, Campaign, CampaignReport, UserProfile
from django.db.models import Sum, Avg


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Account created successfully! Welcome to the dashboard.'
            )
            try:
                profile = user.profile
                if profile.client:
                    return redirect('client_portal')
                return redirect('client_portal')
            except UserProfile.DoesNotExist:
                return redirect('client_portal')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'dashboard/auth/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.client:
                return redirect('client_portal')
            return redirect('client_portal')
        except UserProfile.DoesNotExist:
            return redirect('client_portal')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                try:
                    profile = user.profile
                    if profile.client:
                        return redirect('client_portal')
                    return redirect('client_portal')
                except UserProfile.DoesNotExist:
                    return redirect('client_portal')
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
    reports = CampaignReport.objects.filter(
        campaign=campaign
    ).order_by('-generated_at')

    # Get ML insights if available
    ml_insights = get_ml_insights_for_campaign(campaign)

    context = {
        'campaign': campaign,
        'reports': reports,
        'ml_insights': ml_insights,
        'client': client,
        'profile': profile,
    }
    return render(
        request,
        'dashboard/auth/client_campaign_detail.html',
        context
    )


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

    # Get all reports for this client
    reports = CampaignReport.objects.filter(
        campaign__client=client
    ).order_by('-generated_at')

    # Apply filters if provided
    platform = request.GET.get('platform')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if platform:
        reports = reports.filter(campaign__platform=platform)
    if date_from:
        reports = reports.filter(generated_at__gte=date_from)
    if date_to:
        reports = reports.filter(generated_at__lte=date_to)

    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reports': page_obj,
        'client': client,
        'profile': profile,
        'platform': platform,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'dashboard/auth/client_reports.html', context)


def get_ml_insights_for_campaign(campaign):
    """Get ML insights for a specific campaign"""
    try:
        # This would typically fetch from your ML prediction models
        # For now, return a placeholder
        return {
            'predicted_revenue': campaign.revenue * 1.1,
            'predicted_ctr': campaign.ctr * 1.05,
            'confidence_score': 0.85,
        }
    except Exception:
        return None


@login_required
def admin_clients_view(request):
    """Admin view to manage clients"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    clients = Client.objects.all().order_by('name')
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'clients': page_obj,
        'total_clients': clients.count(),
    }
    return render(request, 'dashboard/admin/clients.html', context)


@login_required
def admin_users_view(request):
    """Admin view to manage users"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    users = User.objects.all().order_by('username')
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'users': page_obj,
        'total_users': users.count(),
    }
    return render(request, 'dashboard/admin/users.html', context)
