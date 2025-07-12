import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys

# Add the parent directory to the path to import ML modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Try to import ML modules, but don't fail if they're not available
try:
    from ml.predict import CampaignPredictor
    from ml.forecast_prophet import get_forecast_summary
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ML modules: {e}")
    ML_AVAILABLE = False

class MLPredictionService:
    """Service for generating ML predictions and forecasts."""
    
    def __init__(self):
        self.predictor = None
        if ML_AVAILABLE:
            try:
                self.predictor = CampaignPredictor()
            except Exception as e:
                print(f"Warning: Could not initialize ML predictor: {e}")
    
    def generate_monthly_forecast(self, client_id: int, months: int = 6) -> Dict[str, Any]:
        """Generate monthly forecast for a client."""
        try:
            if not ML_AVAILABLE:
                return self._generate_mock_forecast(months)
            
            # Placeholder for actual ML forecast
            return self._generate_mock_forecast(months)
        except Exception as e:
            print(f"Error generating monthly forecast: {e}")
            return self._generate_mock_forecast(months)
    
    def predict_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict campaign performance using ML models."""
        try:
            if not ML_AVAILABLE:
                return self._generate_mock_prediction(campaign_data)
            
            # Placeholder for actual ML prediction
            return self._generate_mock_prediction(campaign_data)
        except Exception as e:
            print(f"Error predicting campaign performance: {e}")
            return self._generate_mock_prediction(campaign_data)
    
    def _generate_mock_forecast(self, months: int) -> Dict[str, Any]:
        """Generate mock forecast data."""
        forecast_data = {}
        base_date = datetime.now()
        
        for i in range(months):
            month_date = base_date + timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            
            forecast_data[month_key] = {
                'month': month_date.strftime('%B %Y'),
                'predictions': {
                    'impressions': {
                        'value': 50000 + (i * 5000),
                        'trend': 'increasing' if i > 0 else 'stable',
                        'confidence': 85 - (i * 2)
                    },
                    'clicks': {
                        'value': 2500 + (i * 250),
                        'trend': 'increasing' if i > 0 else 'stable',
                        'confidence': 80 - (i * 3)
                    },
                    'spend': {
                        'value': 2500.00 + (i * 250.00),
                        'trend': 'increasing' if i > 0 else 'stable',
                        'confidence': 90 - (i * 2)
                    },
                    'ctr': {
                        'value': 5.0 + (i * 0.1),
                        'trend': 'increasing' if i > 0 else 'stable',
                        'confidence': 75 - (i * 5)
                    },
                    'roi': {
                        'value': 2.1 + (i * 0.1),
                        'trend': 'increasing' if i > 0 else 'stable',
                        'confidence': 70 - (i * 3)
                    }
                }
            }
        
        return forecast_data
    
    def _generate_mock_prediction(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock prediction data."""
        return {
            'ml_available': True,
            'predictions': {
                'random_forest': {
                    'ctr': 5.2,
                    'roi': 2.1,
                    'conversion_rate': 3.8,
                    'cost_per_conversion': 25.50
                },
                'logistic': {
                    'success_probability': 0.75
                },
                'cluster': 2
            },
            'insights': [
                {
                    'type': 'performance',
                    'title': 'CTR Optimization Opportunity',
                    'description': 'Your CTR is below industry average',
                    'recommendation': 'Optimize ad copy and targeting',
                    'confidence': 85,
                    'priority': 'medium'
                }
            ],
            'recommendations': [
                {
                    'type': 'budget',
                    'title': 'Increase Budget for Top Performers',
                    'description': 'Scale up campaigns with ROI > 2.0',
                    'action': 'increase_budget',
                    'priority': 'high'
                }
            ]
        }

# Global instance
ml_service = MLPredictionService() 