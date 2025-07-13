import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any
import os
import sys
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

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
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.model_accuracy = {}
        self.last_training_date = None

        if ML_AVAILABLE:
            try:
                self.predictor = CampaignPredictor()
            except Exception as e:
                print(f"Warning: Could not initialize ML predictor: {e}")

    def auto_train_models(self, client_id: int = None):
        """Automatically train ML models when new data is available."""
        try:
            from dashboard.models import Campaign

            # Get campaign data
            if client_id:
                campaigns = Campaign.objects.filter(client_id=client_id)
            else:
                campaigns = Campaign.objects.all()

            if campaigns.count() < 10:
                print("Not enough data for training. Need at least 10 campaigns.")
                return False

            # Prepare training data
            X, y_ctr, y_roi, y_conversion = self._prepare_training_data(campaigns)

            if len(X) < 10:
                print("Not enough samples for training.")
                return False

            # Train models
            self._train_ctr_model(X, y_ctr)
            self._train_roi_model(X, y_roi)
            self._train_conversion_model(X, y_conversion)

            # Save models
            self._save_models()

            # Update training date
            self.last_training_date = datetime.now()

            print(f"✅ Models trained successfully on {len(X)} samples")
            print(f"📊 Model Accuracies: {self.model_accuracy}")

            return True

        except Exception as e:
            print(f"❌ Error in auto training: {e}")
            return False

    def _prepare_training_data(self, campaigns):
        """Prepare training data from campaign objects."""
        data = []
        ctr_targets = []
        roi_targets = []
        conversion_targets = []

        for campaign in campaigns:
            try:
                # Features
                features = {
                    'impressions': float(campaign.impressions or 0),
                    'clicks': float(campaign.clicks or 0),
                    'spend': float(campaign.spend or 0),
                    'budget': float(campaign.budget or 0),
                    'platform_google': 1 if campaign.platform == 'google_ads' else 0,
                    'platform_linkedin': 1 if campaign.platform == 'linkedin_ads' else 0,
                    'platform_mailchimp': 1 if campaign.platform == 'mailchimp' else 0,
                    'status_active': 1 if campaign.status == 'active' else 0,
                    'days_running': (
                        (campaign.end_date - campaign.start_date).days
                        if campaign.end_date and campaign.start_date else 30
                    ),
                }

                # Calculate derived features
                features['ctr'] = (
                    (campaign.clicks / campaign.impressions)
                    if campaign.impressions > 0 else 0
                )
                features['cpc'] = (
                    (campaign.spend / campaign.clicks)
                    if campaign.clicks > 0 else 0
                )
                features['cpm'] = (
                    (campaign.spend / campaign.impressions * 1000)
                    if campaign.impressions > 0 else 0
                )

                data.append(features)

                # Targets
                ctr_targets.append(features['ctr'])
                roi_targets.append(float(campaign.roi or 0))
                conversion_targets.append(float(campaign.conversion_rate or 0))

            except Exception as e:
                print(f"Skipping campaign {campaign.id}: {e}")
                continue

        if not data:
            return [], [], [], []

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Handle missing values
        df = df.fillna(0)

        # Remove outliers
        df = self._remove_outliers(df)

        return (
            df.values, np.array(ctr_targets),
            np.array(roi_targets), np.array(conversion_targets)
        )

    def _remove_outliers(self, df, threshold=3):
        """Remove outliers using IQR method."""
        for column in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            df = df[
                (df[column] >= lower_bound) & (df[column] <= upper_bound)
            ]
        return df

    def _train_ctr_model(self, X, y):
        """Train CTR prediction model."""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = model.score(X_test_scaled, y_test)

            # Store model and metrics
            self.models['ctr'] = model
            self.scalers['ctr'] = scaler
            self.model_accuracy['ctr'] = {
                'mse': mse,
                'r2': r2,
                'feature_importance': dict(
                    zip(
                        [f'feature_{i}' for i in range(X.shape[1])],
                        model.feature_importances_
                    )
                )
            }

        except Exception as e:
            print(f"Error training CTR model: {e}")

    def _train_roi_model(self, X, y):
        """Train ROI prediction model."""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = model.score(X_test_scaled, y_test)

            # Store model and metrics
            self.models['roi'] = model
            self.scalers['roi'] = scaler
            self.model_accuracy['roi'] = {
                'mse': mse,
                'r2': r2,
                'feature_importance': dict(
                    zip(
                        [f'feature_{i}' for i in range(X.shape[1])],
                        model.feature_importances_
                    )
                )
            }

        except Exception as e:
            print(f"Error training ROI model: {e}")

    def _train_conversion_model(self, X, y):
        """Train conversion rate prediction model."""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = model.score(X_test_scaled, y_test)

            # Store model and metrics
            self.models['conversion'] = model
            self.scalers['conversion'] = scaler
            self.model_accuracy['conversion'] = {
                'mse': mse,
                'r2': r2,
                'feature_importance': dict(
                    zip(
                        [f'feature_{i}' for i in range(X.shape[1])],
                        model.feature_importances_
                    )
                )
            }

        except Exception as e:
            print(f"Error training conversion model: {e}")

    def _save_models(self):
        """Save trained models to disk."""
        try:
            models_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'ml', 'models'
            )
            os.makedirs(models_dir, exist_ok=True)

            for model_name, model in self.models.items():
                model_path = os.path.join(models_dir, f'{model_name}_model.pkl')
                scaler_path = os.path.join(models_dir, f'{model_name}_scaler.pkl')
                joblib.dump(model, model_path)
                joblib.dump(self.scalers[model_name], scaler_path)

            # Save accuracy metrics
            accuracy_path = os.path.join(models_dir, 'model_accuracy.json')
            import json
            with open(accuracy_path, 'w') as f:
                json.dump(self.model_accuracy, f, indent=2)

        except Exception as e:
            print(f"Error saving models: {e}")

    def load_models(self):
        """Load trained models from disk."""
        try:
            models_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'ml', 'models'
            )

            for model_name in ['ctr', 'roi', 'conversion']:
                model_path = os.path.join(models_dir, f'{model_name}_model.pkl')
                scaler_path = os.path.join(models_dir, f'{model_name}_scaler.pkl')

                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[model_name] = joblib.load(model_path)
                    self.scalers[model_name] = joblib.load(scaler_path)

            # Load accuracy metrics
            accuracy_path = os.path.join(models_dir, 'model_accuracy.json')
            if os.path.exists(accuracy_path):
                import json
                with open(accuracy_path, 'r') as f:
                    self.model_accuracy = json.load(f)

        except Exception as e:
            print(f"Error loading models: {e}")

    def predict_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict campaign performance metrics."""
        try:
            # Extract features
            features = self._extract_features(campaign_data)

            # Make predictions
            predictions = {}
            for metric in ['ctr', 'roi', 'conversion']:
                if metric in self.models and metric in self.scalers:
                    model = self.models[metric]
                    scaler = self.scalers[metric]
                    features_scaled = scaler.transform([features])
                    pred = model.predict(features_scaled)[0]
                    predictions[f'predicted_{metric}'] = max(0, pred)

            # Generate insights
            insights = self._generate_insights(predictions, campaign_data)

            return {
                'predictions': predictions,
                'insights': insights,
                'confidence': self._calculate_confidence(predictions),
                'model_accuracy': self.model_accuracy
            }

        except Exception as e:
            print(f"Error in campaign prediction: {e}")
            return {
                'predictions': {},
                'insights': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def _extract_features(self, campaign_data):
        """Extract features from campaign data."""
        features = [
            float(campaign_data.get('impressions', 0)),
            float(campaign_data.get('clicks', 0)),
            float(campaign_data.get('spend', 0)),
            float(campaign_data.get('budget', 0)),
            1 if campaign_data.get('platform') == 'google_ads' else 0,
            1 if campaign_data.get('platform') == 'linkedin_ads' else 0,
            1 if campaign_data.get('platform') == 'mailchimp' else 0,
            1 if campaign_data.get('status') == 'active' else 0,
            float(campaign_data.get('days_running', 30)),
        ]

        # Add derived features
        impressions = float(campaign_data.get('impressions', 0))
        clicks = float(campaign_data.get('clicks', 0))
        spend = float(campaign_data.get('spend', 0))

        ctr = (clicks / impressions) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0
        cpm = (spend / impressions * 1000) if impressions > 0 else 0

        features.extend([ctr, cpc, cpm])

        return features

    def _generate_insights(self, predictions, campaign_data):
        """Generate insights from predictions."""
        insights = []

        if 'predicted_ctr' in predictions:
            current_ctr = float(campaign_data.get('ctr', 0))
            predicted_ctr = predictions['predicted_ctr']
            if predicted_ctr > current_ctr * 1.1:
                insights.append("CTR is expected to improve significantly")
            elif predicted_ctr < current_ctr * 0.9:
                insights.append("CTR may decline, consider optimization")

        if 'predicted_roi' in predictions:
            current_roi = float(campaign_data.get('roi', 0))
            predicted_roi = predictions['predicted_roi']
            if predicted_roi > current_roi * 1.2:
                insights.append("ROI is expected to increase substantially")
            elif predicted_roi < current_roi * 0.8:
                insights.append("ROI may decrease, review strategy")

        return insights

    def _calculate_confidence(self, predictions):
        """Calculate confidence score for predictions."""
        if not predictions:
            return 0.0

        # Simple confidence based on model accuracy
        avg_accuracy = sum(
            self.model_accuracy.get(metric, {}).get('r2', 0.5)
            for metric in ['ctr', 'roi', 'conversion']
        ) / 3

        return min(1.0, max(0.0, avg_accuracy))

    def generate_monthly_forecast(self, client_id: int, months: int = 6) -> Dict[str, Any]:
        """Generate monthly forecast for a client."""
        try:
            from dashboard.models import Campaign, Client

            client = Client.objects.get(id=client_id)
            campaigns = Campaign.objects.filter(client=client)

            if campaigns.count() < 5:
                return {
                    'error': 'Not enough data for forecasting',
                    'forecast': {}
                }

            # Prepare historical data
            historical_data = []
            for campaign in campaigns:
                historical_data.append({
                    'date': campaign.start_date,
                    'spend': float(campaign.spend),
                    'revenue': float(campaign.revenue),
                    'impressions': int(campaign.impressions),
                    'clicks': int(campaign.clicks),
                    'conversions': int(campaign.conversions),
                })

            # Generate forecast using Prophet if available
            if ML_AVAILABLE:
                try:
                    forecast = get_forecast_summary(historical_data, months)
                    return {
                        'forecast': forecast,
                        'client': client.name,
                        'months': months
                    }
                except Exception as e:
                    print(f"Error in Prophet forecast: {e}")

            # Fallback to simple forecasting
            return self._simple_forecast(historical_data, months)

        except Exception as e:
            print(f"Error in monthly forecast: {e}")
            return {
                'error': str(e),
                'forecast': {}
            }

    def _simple_forecast(self, historical_data, months):
        """Simple forecasting using moving averages."""
        if not historical_data:
            return {'forecast': {}}

        # Calculate averages
        avg_spend = sum(d['spend'] for d in historical_data) / len(historical_data)
        avg_revenue = sum(d['revenue'] for d in historical_data) / len(historical_data)
        avg_impressions = sum(d['impressions'] for d in historical_data) / len(historical_data)

        # Generate simple forecast
        forecast = []
        for i in range(1, months + 1):
            forecast.append({
                'month': i,
                'predicted_spend': avg_spend * (1 + 0.05 * i),  # 5% growth
                'predicted_revenue': avg_revenue * (1 + 0.08 * i),  # 8% growth
                'predicted_impressions': avg_impressions * (1 + 0.03 * i),  # 3% growth
                'confidence': max(0.5, 1.0 - (i * 0.1))  # Decreasing confidence
            })

        return {
            'forecast': forecast,
            'method': 'simple_moving_average',
            'confidence': 'medium'
        } 



