"""
Django management command to start background syncs.
"""

from django.core.management.base import BaseCommand
from dashboard.tasks import sync_all_platform_data, cleanup_old_data, refresh_expired_tokens
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start background sync tasks for all platforms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            choices=['google_ads', 'linkedin_ads', 'mailchimp', 'zoho', 'demandbase', 'all'],
            default='all',
            help='Platform to sync (default: all)'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Run cleanup task'
        )
        parser.add_argument(
            '--refresh-tokens',
            action='store_true',
            help='Refresh expired tokens'
        )

    def handle(self, *args, **options):
        platform = options['platform']
        cleanup = options['cleanup']
        refresh_tokens = options['refresh_tokens']

        if cleanup:
            self.stdout.write('Running cleanup task...')
            try:
                result = cleanup_old_data.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'Cleanup task started: {result.id}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Cleanup task failed: {str(e)}')
                )

        if refresh_tokens:
            self.stdout.write('Running token refresh task...')
            try:
                result = refresh_expired_tokens.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'Token refresh task started: {result.id}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Token refresh task failed: {str(e)}')
                )

        if platform == 'all':
            self.stdout.write('Starting sync for all platforms...')
            try:
                result = sync_all_platform_data.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'All platform sync task started: {result.id}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'All platform sync task failed: {str(e)}')
                )
        else:
            # Import individual sync tasks
            from dashboard.tasks import (
                sync_google_ads_data, sync_linkedin_ads_data, sync_mailchimp_data,
                sync_zoho_data, sync_demandbase_data
            )
            
            task_map = {
                'google_ads': sync_google_ads_data,
                'linkedin_ads': sync_linkedin_ads_data,
                'mailchimp': sync_mailchimp_data,
                'zoho': sync_zoho_data,
                'demandbase': sync_demandbase_data
            }
            
            if platform in task_map:
                self.stdout.write(f'Starting sync for {platform}...')
                try:
                    result = task_map[platform].delay()
                    self.stdout.write(
                        self.style.SUCCESS(f'{platform} sync task started: {result.id}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'{platform} sync task failed: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unknown platform: {platform}')
                )

        self.stdout.write(
            self.style.SUCCESS('Background sync tasks initiated successfully!')
        ) 