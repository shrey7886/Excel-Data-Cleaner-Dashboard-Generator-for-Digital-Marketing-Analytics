import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, Any, Optional

class CampaignPredictor:
    """Unified class for making predictions using all trained models."""
    
    def __init__(self):
        self.models = {}
        self.load_all_models()
    
    def load_all_models(self):
        """Load all trained models."""
        model_files = {
            'random_forest': 'ml/trained_models.pkl',
            'xgboost': 'ml/xgboost_models.pkl',
            'logistic': 'ml/logistic_models.pkl',
            'prophet': 'ml/prophet_models.pkl',
            'kmeans': 'ml/kmeans_models.pkl'
        }
        
        for model_type, file_path in model_files.items():
            try:
                with open(file_path, 'rb') as f:
                    self.models[model_type] = pickle.load(f)
                print(f"Loaded {model_type} models")
            except FileNotFoundError:
                print(f"Warning: {model_type} models not found at {file_path}")
    
    def predict_ctr_roi_cpa(self, campaign_data: Dict[str, Any]) -> Dict[str, float]:
        """Predict CTR, ROI, and CPA using Random Forest."""
        if 'random_forest' not in self.models:
            return {}
        
        try:
            model_data = self.models['random_forest']
            
            # Prepare features
            features = ['platform', 'spend', 'impressions']
            if 'demographic' in campaign_data:
                features.append('demographic')
            if 'intent_score' in campaign_data:
                features.append('intent_score')
            
            # Create feature vector
            X = pd.DataFrame([campaign_data])
            
            # Encode categorical variables
            if 'platform' in model_data['label_encoders']:
                le_platform = model_data['label_encoders']['platform']
                X['platform_encoded'] = le_platform.transform(X['platform'])
            
            if 'demographic' in X.columns and model_data['label_encoders']['demographic']:
                le_demo = model_data['label_encoders']['demographic']
                X['demographic_encoded'] = le_demo.transform(X['demographic'].fillna('Unknown'))
            
            # Select final features
            feature_cols = model_data['feature_cols']
            X_final = X[feature_cols]
            
            # Make predictions
            predictions = {}
            for target_name, model in model_data['models'].items():
                if target_name in ['ctr', 'cpa', 'roi']:
                    pred = model.predict(X_final)[0]
                    predictions[target_name] = max(0, pred)  # Ensure non-negative
            
            return predictions
        
        except Exception as e:
            print(f"Error predicting CTR/ROI/CPA: {e}")
            return {}
    
    def predict_performance_category(self, campaign_data: Dict[str, Any]) -> Dict[str, float]:
        """Predict binary outcomes using Logistic Regression."""
        if 'logistic' not in self.models:
            return {}
        
        try:
            model_data = self.models['logistic']
            
            # Prepare features
            features = ['platform', 'spend', 'impressions']
            if 'demographic' in campaign_data:
                features.append('demographic')
            if 'intent_score' in campaign_data:
                features.append('intent_score')
            
            X = pd.DataFrame([campaign_data])
            
            # Encode categorical variables
            if 'platform' in model_data['label_encoders']:
                le_platform = model_data['label_encoders']['platform']
                X['platform_encoded'] = le_platform.transform(X['platform'])
            
            if 'demographic' in X.columns and model_data['label_encoders']['demographic']:
                le_demo = model_data['label_encoders']['demographic']
                X['demographic_encoded'] = le_demo.transform(X['demographic'].fillna('Unknown'))
            
            # Select final features
            feature_cols = model_data['feature_cols']
            X_final = X[feature_cols]
            
            # Scale features
            X_scaled = model_data['scaler'].transform(X_final)
            
            # Make predictions
            predictions = {}
            for target_name, model in model_data['models'].items():
                prob = model.predict_proba(X_scaled)[0][1]  # Probability of positive class
                predictions[target_name] = prob
            
            return predictions
        
        except Exception as e:
            print(f"Error predicting performance category: {e}")
            return {}
    
    def predict_cluster(self, campaign_data: Dict[str, Any]) -> Optional[int]:
        """Predict cluster using KMeans."""
        if 'kmeans' not in self.models:
            return None
        
        try:
            from ml.cluster_kmeans import predict_cluster
            return predict_cluster(pd.DataFrame([campaign_data]))
        
        except Exception as e:
            print(f"Error predicting cluster: {e}")
            return None
    
    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get Prophet forecast summary."""
        if 'prophet' not in self.models:
            return {}
        
        try:
            from ml.forecast_prophet import get_forecast_summary
            return get_forecast_summary()
        
        except Exception as e:
            print(f"Error getting forecast summary: {e}")
            return {}
    
    def predict_all(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make all predictions for a campaign."""
        results = {
            'campaign_data': campaign_data,
            'predictions': {}
        }
        
        # Random Forest predictions
        rf_predictions = self.predict_ctr_roi_cpa(campaign_data)
        results['predictions']['random_forest'] = rf_predictions
        
        # Logistic Regression predictions
        lr_predictions = self.predict_performance_category(campaign_data)
        results['predictions']['logistic'] = lr_predictions
        
        # KMeans cluster prediction
        cluster = self.predict_cluster(campaign_data)
        results['predictions']['cluster'] = cluster
        
        # Prophet forecasts
        forecasts = self.get_forecast_summary()
        results['predictions']['forecasts'] = forecasts
        
        return results

def predict_campaign_performance(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to predict campaign performance."""
    predictor = CampaignPredictor()
    return predictor.predict_all(campaign_data)

if __name__ == "__main__":
    # Example usage
    sample_campaign = {
        'platform': 'Google Ads',
        'spend': 1000,
        'impressions': 50000,
        'demographic': 'IT',
        'intent_score': 75
    }
    
    predictions = predict_campaign_performance(sample_campaign)
    print("Campaign Performance Predictions:")
    print(predictions) 