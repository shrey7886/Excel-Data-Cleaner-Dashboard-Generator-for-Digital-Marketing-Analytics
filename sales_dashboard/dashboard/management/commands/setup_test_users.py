from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from dashboard.models import Client, UserProfile

class Command(BaseCommand):
    help = 'Set up test users for the application'

    def handle(self, *args, **options):
        # Create or update admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@targetorate.com',
                'is_staff': True,
                'is_superuser': True,
                'password': make_password('admin123')
            }
        )
        if not created:
            admin_user.password = make_password('admin123')
            admin_user.save()
        
        # Create or update client user
        client_user, created = User.objects.get_or_create(
            username='techflow_client',
            defaults={
                'first_name': 'TechFlow',
                'last_name': 'Client',
                'email': 'client@techflow.com',
                'password': make_password('client123')
            }
        )
        if not created:
            client_user.password = make_password('client123')
            client_user.save()
        
        # Create or update client
        client, created = Client.objects.get_or_create(
            company='TechFlow Solutions',
            defaults={
                'contact_person': 'John Smith',
                'email': 'contact@techflow.com',
                'phone': '+1-555-0123',
                'industry': 'Technology',
                'website': 'https://techflow.com'
            }
        )
        
        # Create or update user profile for client user
        profile, created = UserProfile.objects.get_or_create(
            user=client_user,
            defaults={
                'client': client,
                'role': 'client',
                'phone': '+1-555-0124'
            }
        )
        if not created:
            profile.client = client
            profile.role = 'client'
            profile.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up test users:\n'
                f'Admin: username=admin, password=admin123\n'
                f'Client: username=techflow_client, password=client123'
            )
        ) 