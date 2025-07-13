from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from sales_dashboard.dashboard.models import UserProfile, Client


class Command(BaseCommand):
    help = 'Create a new TechFlow user with associated profile'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('email', type=str, help='Email for the new user')
        parser.add_argument('password', type=str, help='Password for the new user')
        parser.add_argument('--client', type=str, help='Client name for the user')
        parser.add_argument('--is-staff', action='store_true', help='Make user staff')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        client_name = options.get('client')
        is_staff = options.get('is_staff', False)

        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=is_staff
                )

                # Create or get client if specified
                client = None
                if client_name:
                    client, created = Client.objects.get_or_create(
                        name=client_name,
                        defaults={'description': f'Client for {client_name}'}
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created new client: {client_name}')
                        )

                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    client=client,
                    role='client' if client else 'admin'
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created user {username} with profile'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating user: {str(e)}')
            ) 

