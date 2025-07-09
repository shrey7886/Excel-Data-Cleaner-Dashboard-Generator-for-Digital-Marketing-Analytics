import os
import csv
from django.core.management.base import BaseCommand
from dashboard.models import Client, Campaign, CampaignReport
from django.utils.dateparse import parse_date
from django.conf import settings

class Command(BaseCommand):
    help = 'Load demo data from output/unified_campaign_data.csv into the database.'

    def handle(self, *args, **kwargs):
        client, _ = Client.objects.get_or_create(
            name='Demo Client',
            defaults={'email': 'demo@example.com', 'organization': 'Demo Org'}
        )
        project_root = os.path.dirname(settings.BASE_DIR)
        csv_path = os.path.abspath(os.path.join(project_root, 'output', 'unified_campaign_data.csv'))
        self.stdout.write(f"Resolved CSV path: {csv_path}")
        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                campaign, _ = Campaign.objects.get_or_create(
                    client=client,
                    name=row['campaign_name'],
                    platform=row['platform'],
                    defaults={
                        'start_date': parse_date(row['date']) or '2024-01-01',
                        'end_date': None
                    }
                )
                CampaignReport.objects.create(
                    campaign=campaign,
                    report_date=parse_date(row['date']) or '2024-01-01',
                    impressions=row.get('impressions') or None,
                    clicks=row.get('clicks') or None,
                    spend=row.get('spend') or None,
                    open_rate=row.get('open_rate') or None,
                    click_rate=row.get('click_rate') or None,
                    conversions=row.get('conversions') or None,
                    leads=row.get('leads') or None,
                    deals=row.get('deals') or None,
                    intent_score=row.get('intent_score') or None,
                    cpl=row.get('cpl') or None,
                    demographic=row.get('demographic') or None,
                )
        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully.')) 