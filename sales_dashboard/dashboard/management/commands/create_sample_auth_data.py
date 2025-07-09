from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Client, Campaign, UserProfile
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample authentication data with clients and campaigns'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample authentication data...')
        
        # Create sample clients
        clients_data = [
            {
                'name': 'John Smith',
                'email': 'john@techstartup.com',
                'company': 'TechStartup Inc.',
                'phone': '+1-555-0101',
                'address': '123 Innovation Drive, Silicon Valley, CA'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah@marketingpro.com',
                'company': 'MarketingPro Solutions',
                'phone': '+1-555-0102',
                'address': '456 Business Ave, New York, NY'
            },
            {
                'name': 'Mike Chen',
                'email': 'mike@ecommercehub.com',
                'company': 'E-Commerce Hub',
                'phone': '+1-555-0103',
                'address': '789 Digital Street, Austin, TX'
            }
        ]
        
        clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            clients.append(client)
            if created:
                self.stdout.write(f'Created client: {client.company}')
        
        # Create sample users for each client
        users_data = [
            {
                'username': 'john_tech',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@techstartup.com',
                'password': 'password123',
                'role': 'manager',
                'department': 'Marketing'
            },
            {
                'username': 'sarah_marketing',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah@marketingpro.com',
                'password': 'password123',
                'role': 'analyst',
                'department': 'Digital Marketing'
            },
            {
                'username': 'mike_ecommerce',
                'first_name': 'Mike',
                'last_name': 'Chen',
                'email': 'mike@ecommercehub.com',
                'password': 'password123',
                'role': 'viewer',
                'department': 'Sales'
            }
        ]
        
        for i, user_data in enumerate(users_data):
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Create user profile
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'client': clients[i],
                        'role': user_data['role'],
                        'department': user_data['department'],
                        'is_client_user': True
                    }
                )
                
                self.stdout.write(f'Created user: {user.username} for {clients[i].company}')
        
        # Create sample campaigns for each client
        platforms = ['mailchimp', 'google_ads', 'linkedin_ads', 'zoho', 'demandbase']
        statuses = ['active', 'paused', 'completed']
        
        for client in clients:
            # Create 3-5 campaigns per client
            num_campaigns = random.randint(3, 5)
            
            for i in range(num_campaigns):
                start_date = date.today() - timedelta(days=random.randint(30, 180))
                end_date = start_date + timedelta(days=random.randint(30, 90))
                
                impressions = random.randint(10000, 100000)
                clicks = random.randint(100, 5000)
                spend = random.uniform(500, 5000)
                conversions = random.randint(10, 200)
                
                # Calculate KPIs
                ctr = (clicks / impressions) * 100 if impressions > 0 else 0
                cpc = spend / clicks if clicks > 0 else 0
                cpm = (spend / impressions) * 1000 if impressions > 0 else 0
                conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
                cost_per_conversion = spend / conversions if conversions > 0 else 0
                revenue = conversions * random.uniform(50, 200)  # Assume $50-200 per conversion
                roi = ((revenue - spend) / spend) * 100 if spend > 0 else 0
                
                campaign = Campaign.objects.create(
                    name=f"{client.company} Campaign {i+1}",
                    platform=random.choice(platforms),
                    status=random.choice(statuses),
                    start_date=start_date,
                    end_date=end_date,
                    budget=spend * 1.2,  # Budget 20% higher than spend
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    spend=spend,
                    ctr=ctr,
                    cpc=cpc,
                    cpm=cpm,
                    conversion_rate=conversion_rate,
                    cost_per_conversion=cost_per_conversion,
                    roi=roi,
                    revenue=revenue,
                    client=client
                )
                
                self.stdout.write(f'Created campaign: {campaign.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(clients)} clients, {len(users_data)} users, and {Campaign.objects.count()} campaigns!'
            )
        )
        
        self.stdout.write('\nSample login credentials:')
        self.stdout.write('Admin: admin / admin123')
        for user_data in users_data:
            self.stdout.write(f'{user_data["username"]}: {user_data["username"]} / {user_data["password"]}') 