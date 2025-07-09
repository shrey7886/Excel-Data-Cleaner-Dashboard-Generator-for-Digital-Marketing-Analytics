from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from dashboard.models import Client, UserProfile
from datetime import datetime

class Command(BaseCommand):
    help = 'Set up default users and clients for the Targetorate dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Setting up users and clients...')
        
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create(
                username='admin',
                email='admin@targetorate.com',
                password=make_password('admin123'),
                is_staff=True,
                is_superuser=True,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin/admin123'))
        else:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Updated admin password: admin/admin123'))
        
        # Create clients
        clients_data = [
            {
                'name': 'John Smith',
                'email': 'john@techflow.com',
                'company': 'TechFlow Solutions',
                'phone': '+1-555-0123',
                'address': '123 Tech Street, Silicon Valley, CA 94025'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah@innovatecorp.com',
                'company': 'InnovateCorp',
                'phone': '+1-555-0456',
                'address': '456 Innovation Ave, Austin, TX 73301'
            }
        ]
        
        for i, client_data in enumerate(clients_data, 1):
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created client: {client.company}'))
            
            # Create user for this client
            username = f'client{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create(
                    username=username,
                    email=client_data['email'],
                    password=make_password('password123'),
                    first_name=client_data['name'].split()[0],
                    last_name=client_data['name'].split()[1]
                )
                
                # Create user profile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'client': client,
                        'role': 'client_admin',
                        'is_client_user': True,
                        'phone': client_data['phone']
                    }
                )
                
                if not created:
                    profile.client = client
                    profile.save()
                
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}/password123 for {client.company}'))
            else:
                user = User.objects.get(username=username)
                user.set_password('password123')
                user.save()
                
                profile = UserProfile.objects.get(user=user)
                profile.client = client
                profile.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated user: {username}/password123 for {client.company}'))
        
        self.stdout.write(self.style.SUCCESS('User setup completed successfully!'))
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('Admin: admin/admin123')
        self.stdout.write('Client 1: client1/password123')
        self.stdout.write('Client 2: client2/password123') 