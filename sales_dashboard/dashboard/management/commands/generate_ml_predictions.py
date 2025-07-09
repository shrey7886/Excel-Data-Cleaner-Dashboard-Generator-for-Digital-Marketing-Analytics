from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from dashboard.models import Client, Campaign, MLPrediction, FutureForecast
from dashboard.services import ml_service
import random

class Command(BaseCommand):
    help = 'Generate sample ML predictions and forecasts for clients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=int,
            help='Generate predictions for specific client ID',
        )
        parser.add_argument(
            '--all-clients',
            action='store_true',
            help='Generate predictions for all clients',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ML prediction generation...'))
        
        # Get clients
        if options['client_id']:
            clients = Client.objects.filter(id=options['client_id'])
        elif options['all_clients']:
            clients = Client.objects.all()
        else:
            clients = Client.objects.all()[:3]  # Default to first 3 clients
        
        for client in clients:
            self.stdout.write(f'Generating predictions for client: {client.name}')
            
            # Generate campaign predictions
            campaigns = Campaign.objects.filter(client=client)
            for campaign in campaigns:
                # Skip campaigns with invalid decimals
                try:
                    # Ensure budget, spend, and revenue are valid decimals
                    if campaign.budget is None or campaign.spend is None or campaign.revenue is None:
                        self.stdout.write(self.style.WARNING(f'Skipping campaign {campaign.name} due to missing decimal fields.'))
                        continue
                    # Try to cast to float to catch invalid values
                    float(campaign.budget)
                    float(campaign.spend)
                    float(campaign.revenue)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Skipping campaign {campaign.name} due to invalid decimal: {e}'))
                    continue
                self.generate_campaign_prediction(campaign)
            
            # Generate monthly forecasts
            self.generate_monthly_forecasts(client)
            
            # Generate future forecasts
            self.generate_future_forecasts(client)
        
        self.stdout.write(self.style.SUCCESS('ML prediction generation completed!'))

    def generate_campaign_prediction(self, campaign):
        """Generate ML prediction for a specific campaign."""
        try:
            # Create sample prediction data
            prediction_data = {
                'random_forest': {
                    'ctr': round(random.uniform(0.02, 0.08), 4),
                    'roi': round(random.uniform(1.5, 4.0), 2),
                    'cpa': round(random.uniform(1.0, 3.0), 2)
                },
                'logistic': {
                    'high_performance_probability': round(random.uniform(0.6, 0.9), 3),
                    'profitable_probability': round(random.uniform(0.7, 0.95), 3)
                },
                'cluster': random.randint(0, 2),
                'forecasts': {
                    'impressions': {
                        'trend': random.choice(['increasing', 'decreasing', 'stable']),
                        'change_percent': round(random.uniform(-20, 30), 1)
                    },
                    'clicks': {
                        'trend': random.choice(['increasing', 'decreasing', 'stable']),
                        'change_percent': round(random.uniform(-15, 25), 1)
                    },
                    'spend': {
                        'trend': random.choice(['increasing', 'decreasing', 'stable']),
                        'change_percent': round(random.uniform(-10, 20), 1)
                    }
                }
            }
            
            # Create insights
            insights = [
                {
                    'type': 'optimization',
                    'title': f'Optimize {campaign.platform} Campaign',
                    'description': f'Based on historical data, {campaign.platform} campaigns show 15% better performance with audience targeting.',
                    'recommendation': 'Consider implementing audience targeting for better performance.'
                },
                {
                    'type': 'opportunity',
                    'title': 'Budget Optimization Opportunity',
                    'description': 'Current spend allocation could be optimized for 20% better ROI.',
                    'recommendation': 'Reallocate budget to high-performing ad groups.'
                }
            ]
            
            # Create recommendations
            recommendations = [
                'Increase budget allocation to top-performing keywords',
                'Optimize ad copy based on A/B testing results',
                'Expand targeting to similar audiences',
                'Implement automated bidding strategies'
            ]
            
            # Create or update prediction
            prediction, created = MLPrediction.objects.get_or_create(
                campaign=campaign,
                prediction_type='campaign',
                defaults={
                    'client': campaign.client,
                    'predicted_metrics': prediction_data,
                    'confidence_score': Decimal(str(round(random.uniform(0.75, 0.95), 2))),
                    'model_used': 'ensemble',
                    'model_version': '1.0',
                    'insights': insights,
                    'recommendations': recommendations,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'  Created campaign prediction for: {campaign.name}')
            else:
                self.stdout.write(f'  Updated campaign prediction for: {campaign.name}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating campaign prediction: {e}'))

    def generate_monthly_forecasts(self, client):
        """Generate monthly forecasts for a client."""
        try:
            # Get monthly forecast data from ML service
            forecast_data = ml_service.get_monthly_forecast(3)
            
            for month_key, month_data in forecast_data.items():
                # Create or update monthly forecast prediction
                prediction, created = MLPrediction.objects.get_or_create(
                    client=client,
                    prediction_type='monthly_forecast',
                    target_date=datetime.strptime(month_key, '%Y-%m').date(),
                    defaults={
                        'predicted_metrics': month_data['predictions'],
                        'confidence_score': Decimal(str(round(random.uniform(0.7, 0.9), 2))),
                        'model_used': 'prophet',
                        'model_version': '1.0',
                        'insights': [
                            {
                                'type': 'trend_analysis',
                                'title': f'Monthly Trend for {month_data["month"]}',
                                'description': f'Predicted performance trends for {month_data["month"]}',
                                'recommendation': 'Monitor actual performance against predictions.'
                            }
                        ],
                        'recommendations': [
                            'Adjust budget based on predicted performance',
                            'Prepare for seasonal variations',
                            'Optimize campaigns for predicted trends'
                        ],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created monthly forecast for: {month_data["month"]}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating monthly forecasts: {e}'))

    def generate_future_forecasts(self, client):
        """Generate future forecasts for a client."""
        try:
            current_date = timezone.now().date()
            
            for i in range(1, 4):  # Generate 3 months of forecasts
                forecast_date = current_date + timedelta(days=30*i)
                
                # Generate realistic forecast data
                base_impressions = random.randint(50000, 200000)
                base_clicks = int(base_impressions * random.uniform(0.02, 0.06))
                base_spend = random.uniform(3000, 15000)
                base_revenue = base_spend * random.uniform(1.5, 4.0)
                
                # Add some variation based on month
                month_factor = 1.0 + (i * 0.1)  # Slight increase over months
                
                forecast, created = FutureForecast.objects.get_or_create(
                    client=client,
                    forecast_date=forecast_date,
                    defaults={
                        'predicted_impressions': int(base_impressions * month_factor),
                        'predicted_clicks': int(base_clicks * month_factor),
                        'predicted_spend': Decimal(str(round(base_spend * month_factor, 2))),
                        'predicted_revenue': Decimal(str(round(base_revenue * month_factor, 2))),
                        'predicted_conversions': int(base_clicks * random.uniform(0.1, 0.3) * month_factor),
                        'predicted_ctr': Decimal(str(round(random.uniform(0.02, 0.08), 4))),
                        'predicted_roi': Decimal(str(round(base_revenue / base_spend, 2))),
                        'confidence_score': Decimal(str(round(max(0.6, 1.0 - (i * 0.1)), 2))),
                        'trend_direction': random.choice(['increasing', 'decreasing', 'stable']),
                        'trend_strength': Decimal(str(round(random.uniform(0.3, 0.8), 2))),
                        'seasonal_factors': {
                            'season': 'Q1' if forecast_date.month <= 3 else 'Q2' if forecast_date.month <= 6 else 'Q3' if forecast_date.month <= 9 else 'Q4',
                            'holiday_impact': random.choice(['low', 'medium', 'high'])
                        },
                        'market_conditions': {
                            'competition_level': random.choice(['low', 'medium', 'high']),
                            'market_trend': random.choice(['growing', 'stable', 'declining'])
                        },
                        'risk_factors': [
                            'Seasonal fluctuations',
                            'Market competition changes',
                            'Platform algorithm updates'
                        ]
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created future forecast for: {forecast_date.strftime("%B %Y")}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating future forecasts: {e}')) 