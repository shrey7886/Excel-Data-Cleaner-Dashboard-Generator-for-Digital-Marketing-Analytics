from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Client, UserProfile, Campaign, GoogleAdsCredential, LinkedInAdsCredential, MailchimpCredential, ZohoCredential
import os
import pandas as pd

class UserRegistrationForm(UserCreationForm):
    """Custom user registration form with client association"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        })
    )
    phone = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)',
            'autocomplete': 'tel'
        })
    )
    company = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name',
            'autocomplete': 'organization'
        })
    )
    department = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department (optional)'
        })
    )
    role = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Role (optional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enhance password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        })
        
        # Add help text
        self.fields['password1'].help_text = """
        <ul class="password-help">
            <li>At least 8 characters long</li>
            <li>Can't be too common</li>
            <li>Can't be entirely numeric</li>
        </ul>
        """
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create or get client
            client, created = Client.objects.get_or_create(
                company=self.cleaned_data['company'],
                defaults={
                    'name': f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}",
                    'email': self.cleaned_data['email'],
                }
            )
            
            # Use provided role or default to 'viewer'
            role = self.cleaned_data.get('role') or 'viewer'
            # Create user profile
            UserProfile.objects.create(
                user=user,
                client=client,
                role=role,
                phone=self.cleaned_data.get('phone', ''),
                department=self.cleaned_data.get('department', ''),
                is_client_user=True
            )
        
        return user

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

class ClientForm(forms.ModelForm):
    """Form for creating and editing clients"""
    class Meta:
        model = Client
        fields = ['name', 'email', 'company', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Person Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Email'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Company Address'
            }),
        }

class UserProfileForm(forms.ModelForm):
    """Form for editing user profiles"""
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'department']
        exclude = ['user', 'client', 'is_client_user']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
        }

class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            if not user:
                # Try with email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if not user:
                raise forms.ValidationError("Invalid username/email or password.")
            elif not user.is_active:
                raise forms.ValidationError("This account is inactive.")
        
        return cleaned_data

class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user found with this email address.")
        return email

class CampaignFilterForm(forms.Form):
    """Form for filtering campaigns in client portal"""
    platform = forms.ChoiceField(
        choices=[('', 'All Platforms')] + Campaign.PLATFORM_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Campaign.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class GoogleAdsCredentialForm(forms.ModelForm):
    class Meta:
        model = GoogleAdsCredential
        fields = ['refresh_token', 'google_client_id', 'client_secret', 'developer_token']
        widgets = {
            'refresh_token': forms.TextInput(attrs={'class': 'form-control'}),
            'google_client_id': forms.TextInput(attrs={'class': 'form-control'}),
            'client_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'developer_token': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LinkedInAdsCredentialForm(forms.ModelForm):
    class Meta:
        model = LinkedInAdsCredential
        fields = ['access_token', 'expires_at']
        widgets = {
            'access_token': forms.TextInput(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class MailchimpCredentialForm(forms.ModelForm):
    class Meta:
        model = MailchimpCredential
        fields = ['api_key', 'server_prefix']
        widgets = {
            'api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'server_prefix': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ZohoCredentialForm(forms.ModelForm):
    class Meta:
        model = ZohoCredential
        fields = ['access_token', 'refresh_token', 'zoho_client_id', 'client_secret']
        widgets = {
            'access_token': forms.TextInput(attrs={'class': 'form-control'}),
            'refresh_token': forms.TextInput(attrs={'class': 'form-control'}),
            'zoho_client_id': forms.TextInput(attrs={'class': 'form-control'}),
            'client_secret': forms.TextInput(attrs={'class': 'form-control'}),
        } 