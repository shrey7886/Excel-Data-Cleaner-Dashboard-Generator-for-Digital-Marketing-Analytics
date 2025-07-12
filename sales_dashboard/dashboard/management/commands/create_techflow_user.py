from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from dashboard.models import Client, UserProfile

class Command(BaseCommand):
    help = 'Create techflow_client user for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating techflow_client user...')
        
        # Create TechFlow client
        client, created = Client.objects.get_or_create(
            email='client@techflow.com',
            defaults={
                'name': 'TechFlow Client',
                'company': 'TechFlow Solutions',
                'phone': '+1-555-0123',
                'address': '123 Tech Street, Silicon Valley, CA 94025'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created client: {client.company}'))
        
        # Create techflow_client user
        if not User.objects.filter(username='techflow_client').exists():
            user = User.objects.create(
                username='techflow_client',
                email='client@techflow.com',
                password=make_password('password123'),
                first_name='TechFlow',
                last_name='Client'
            )
            
            # Create user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'client': client,
                    'role': 'client_admin',
                    'is_client_user': True,
                    'phone': '+1-555-0123'
                }
            )
            
            if not created:
                profile.client = client
                profile.save()
            
            self.stdout.write(self.style.SUCCESS('Created user: techflow_client/password123'))
        else:
            user = User.objects.get(username='techflow_client')
            user.set_password('password123')
            user.save()
            
            profile = UserProfile.objects.get(user=user)
            profile.client = client
            profile.save()
            
            self.stdout.write(self.style.SUCCESS('Updated user: techflow_client/password123'))
        
        self.stdout.write(self.style.SUCCESS('TechFlow user setup completed!'))
        self.stdout.write('Login: techflow_client / password123') 