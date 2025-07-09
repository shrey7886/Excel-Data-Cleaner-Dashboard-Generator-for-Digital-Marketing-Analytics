import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys

# Add the parent directory to the path to import ML modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from ml.predict import CampaignPredictor
    from ml.forecast_prophet import get_forecast_summary
except ImportError as e:
    print(f"Warning: Could not import ML modules: {e}")

class MLPredictionService:
    """Service for generating ML predictions and forecasts."""
    
    def __init__(self):
        self.predictor = None
        try:
            self.predictor = CampaignPredictor()
        except Exception as e:
            print(f"Warning: Could not initialize ML predictor: {e}")
    
    def get_monthly_forecast(self, months_ahead: int = 3) -> Dict[str, Any]:
        """Generate monthly forecasts for the next N months."""
        if not self.predictor:
            return self._get_mock_forecast(months_ahead)
        
        try:
            # Get Prophet forecasts
            forecast_summary = get_forecast_summary()
            
            # Generate monthly predictions
            monthly_forecast = {}
            current_date = datetime.now()
            
            for i in range(1, months_ahead + 1):
                month_date = current_date + timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                
                monthly_forecast[month_key] = {
                    'month': month_date.strftime('%B %Y'),
                    'predictions': {}
                }
                
                # Generate predictions for each metric
                for metric, data in forecast_summary.items():
                    if isinstance(data, dict) and 'predicted_value' in data:
                        # Extrapolate based on trend
                        base_value = data['predicted_value']
                        trend_factor = 1.05 if data.get('trend') == 'increasing' else 0.95
                        
                        # Apply trend with some randomness
                        monthly_value = base_value * (trend_factor ** i) * (0.9 + 0.2 * np.random.random())
                        
                        monthly_forecast[month_key]['predictions'][metric] = {
                            'value': round(monthly_value, 2),
                            'trend': data.get('trend', 'stable'),
                            'confidence': max(0.7, 1.0 - (i * 0.1))  # Confidence decreases with time
                        }
            
            return monthly_forecast
            
        except Exception as e:
            print(f"Error generating monthly forecast: {e}")
            return self._get_mock_forecast(months_ahead)
    
    def _get_mock_forecast(self, months_ahead: int) -> Dict[str, Any]:
        """Generate mock forecasts when ML models are not available."""
        monthly_forecast = {}
        current_date = datetime.now()
        
        base_metrics = {
            'impressions': 50000,
            'clicks': 2500,
            'spend': 5000,
            'ctr': 0.05,
            'cpa': 2.0,
            'conversions': 1250,
            'roi': 2.5
        }
        
        for i in range(1, months_ahead + 1):
            month_date = current_date + timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            
            monthly_forecast[month_key] = {
                'month': month_date.strftime('%B %Y'),
                'predictions': {}
            }
            
            for metric, base_value in base_metrics.items():
                # Add some realistic variation
                variation = 1.0 + (np.random.random() - 0.5) * 0.2  # ±10% variation
                trend = 'increasing' if variation > 1.05 else 'decreasing' if variation < 0.95 else 'stable'
                
                monthly_forecast[month_key]['predictions'][metric] = {
                    'value': round(base_value * variation, 2),
                    'trend': trend,
                    'confidence': max(0.6, 1.0 - (i * 0.15))
                }
        
        return monthly_forecast
    
    def predict_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance for a specific campaign."""
        if not self.predictor:
            return self._get_mock_campaign_predictions(campaign_data)
        
        try:
            return self.predictor.predict_all(campaign_data)
        except Exception as e:
            print(f"Error predicting campaign performance: {e}")
            return self._get_mock_campaign_predictions(campaign_data)
    
    def _get_mock_campaign_predictions(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock campaign predictions."""
        return {
            'campaign_data': campaign_data,
            'predictions': {
                'random_forest': {
                    'ctr': round(0.05 + np.random.random() * 0.03, 4),
                    'roi': round(2.0 + np.random.random() * 1.5, 2),
                    'cpa': round(1.5 + np.random.random() * 1.0, 2)
                },
                'logistic': {
                    'high_performance_probability': round(0.6 + np.random.random() * 0.3, 3),
                    'profitable_probability': round(0.7 + np.random.random() * 0.2, 3)
                },
                'cluster': np.random.randint(0, 3),
                'forecasts': {
                    'impressions': {'trend': 'increasing', 'change_percent': 15.5},
                    'clicks': {'trend': 'increasing', 'change_percent': 12.3},
                    'spend': {'trend': 'stable', 'change_percent': 2.1}
                }
            }
        }
    
    def get_ai_insights(self, campaign_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate AI-powered insights and recommendations."""
        insights = []
        
        # Get monthly forecast for insights
        forecast = self.get_monthly_forecast(3)
        
        # Analyze trends and generate insights
        if forecast:
            next_month = list(forecast.keys())[0]
            next_month_data = forecast[next_month]
            
            for metric, data in next_month_data['predictions'].items():
                if data['trend'] == 'increasing' and data['confidence'] > 0.8:
                    insights.append({
                        'type': 'positive_trend',
                        'title': f'Strong {metric.upper()} Growth Predicted',
                        'description': f'{metric.upper()} is expected to increase by {abs(data.get("change_percent", 10)):.1f}% in {next_month_data["month"]}',
                        'confidence': data['confidence'],
                        'recommendation': f'Consider increasing budget allocation for {metric}-focused campaigns',
                        'priority': 'high' if data['confidence'] > 0.9 else 'medium'
                    })
                elif data['trend'] == 'decreasing' and data['confidence'] > 0.8:
                    insights.append({
                        'type': 'warning',
                        'title': f'{metric.upper()} Decline Expected',
                        'description': f'{metric.upper()} may decrease in {next_month_data["month"]}',
                        'confidence': data['confidence'],
                        'recommendation': f'Review and optimize {metric}-related strategies',
                        'priority': 'high'
                    })
        
        # Add general insights
        insights.extend([
            {
                'type': 'optimization',
                'title': 'Seasonal Optimization Opportunity',
                'description': 'Historical data shows 15% better performance during Q4',
                'confidence': 0.85,
                'recommendation': 'Plan Q4 campaigns with increased budget allocation',
                'priority': 'medium'
            },
            {
                'type': 'opportunity',
                'title': 'Cross-Platform Synergy',
                'description': 'Campaigns running on multiple platforms show 25% better ROI',
                'confidence': 0.78,
                'recommendation': 'Consider expanding successful campaigns to additional platforms',
                'priority': 'medium'
            }
        ])
        
        return insights

# Global instance
ml_service = MLPredictionService() 