import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import pickle
import os

def train_logistic_model():
    """Train Logistic Regression models for binary outcomes."""
    
    # Load unified data
    df = pd.read_csv('output/unified_campaign_data.csv')
    
    # Clean and prepare data
    df = df.dropna(subset=['clicks', 'impressions', 'spend'])
    
    # Calculate target variables
    df['ctr'] = df['clicks'] / df['impressions']
    df['cpa'] = df['spend'] / df['conversions'].fillna(1)
    
    # Binary outcomes
    df['high_ctr'] = (df['ctr'] > df['ctr'].median()).astype(int)  # Above median CTR
    df['low_cpa'] = (df['cpa'] < df['cpa'].median()).astype(int)   # Below median CPA
    df['profitable'] = (df['spend'] < df['clicks'] * 2).astype(int)  # Simple profitability rule
    
    # Prepare features
    features = ['platform', 'spend', 'impressions']
    if 'demographic' in df.columns:
        features.append('demographic')
    if 'intent_score' in df.columns:
        features.append('intent_score')
    
    X = df[features].copy()
    
    # Encode categorical variables
    le_platform = LabelEncoder()
    X['platform_encoded'] = le_platform.fit_transform(X['platform'])
    
    if 'demographic' in X.columns:
        le_demo = LabelEncoder()
        X['demographic_encoded'] = le_demo.fit_transform(X['demographic'].fillna('Unknown'))
    
    # Select final features
    feature_cols = ['platform_encoded', 'spend', 'impressions']
    if 'demographic_encoded' in X.columns:
        feature_cols.append('demographic_encoded')
    if 'intent_score' in X.columns:
        feature_cols.append('intent_score')
    
    X_final = X[feature_cols]
    
    # Scale features for logistic regression
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_final)
    
    # Train models for different binary outcomes
    models = {}
    metrics = {}
    
    for target_name, y in [('high_ctr', df['high_ctr']), ('low_cpa', df['low_cpa']), ('profitable', df['profitable'])]:
        # Remove any NaN values
        mask = ~y.isna()
        X_clean = X_scaled[mask]
        y_clean = y[mask]
        
        if len(X_clean) > 10 and len(np.unique(y_clean)) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y_clean, test_size=0.2, random_state=42, stratify=y_clean
            )
            
            # Logistic Regression
            lr_model = LogisticRegression(random_state=42, max_iter=1000)
            lr_model.fit(X_train, y_train)
            
            y_pred = lr_model.predict(X_test)
            y_pred_proba = lr_model.predict_proba(X_test)[:, 1]
            
            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba)
            
            models[target_name] = lr_model
            metrics[target_name] = {
                'accuracy': accuracy,
                'auc': auc,
                'feature_importance': dict(zip(feature_cols, lr_model.coef_[0]))
            }
            
            print(f"\n{target_name.upper()} Model:")
            print(f"Accuracy: {accuracy:.4f}")
            print(f"AUC: {auc:.4f}")
            print("Classification Report:")
            print(classification_report(y_test, y_pred))
    
    # Save models and preprocessing
    logistic_data = {
        'models': models,
        'scaler': scaler,
        'label_encoders': {
            'platform': le_platform,
            'demographic': le_demo if 'demographic' in X.columns else None
        },
        'feature_cols': feature_cols,
        'metrics': metrics
    }
    
    with open('ml/logistic_models.pkl', 'wb') as f:
        pickle.dump(logistic_data, f)
    
    print("\nLogistic Regression models saved to ml/logistic_models.pkl")
    return logistic_data

if __name__ == "__main__":
    train_logistic_model() 