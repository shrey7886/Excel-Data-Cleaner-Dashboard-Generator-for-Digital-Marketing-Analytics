import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
import pickle
import os
import matplotlib.pyplot as plt

def train_kmeans_models():
    """Train KMeans models for campaign and lead segmentation."""
    
    # Load unified data
    df = pd.read_csv('output/unified_campaign_data.csv')
    
    # Clean and prepare data
    df = df.dropna(subset=['clicks', 'impressions', 'spend'])
    
    # Calculate derived metrics
    df['ctr'] = df['clicks'] / df['impressions']
    df['cpa'] = df['spend'] / df['conversions'].fillna(1)
    df['engagement_rate'] = (df['clicks'] + df['conversions']) / df['impressions']
    
    # Prepare features for clustering
    clustering_features = ['spend', 'impressions', 'clicks', 'ctr', 'cpa', 'engagement_rate']
    
    # Add categorical features if available
    if 'demographic' in df.columns:
        clustering_features.append('demographic')
    if 'intent_score' in df.columns:
        clustering_features.append('intent_score')
    
    X = df[clustering_features].copy()
    
    # Encode categorical variables
    encoders = {}
    if 'demographic' in X.columns:
        le_demo = LabelEncoder()
        X['demographic_encoded'] = le_demo.fit_transform(X['demographic'].fillna('Unknown'))
        encoders['demographic'] = le_demo
        X = X.drop('demographic', axis=1)
    
    # Remove infinite values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.dropna()
    
    if len(X) < 5:
        print("Not enough data for clustering")
        return None
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Determine optimal number of clusters using elbow method
    inertias = []
    K_range = range(2, min(6, len(X) // 2))
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
    
    # Use 3 clusters by default, or optimal from elbow method
    optimal_k = 3 if len(K_range) >= 2 else 2
    
    # Train KMeans model
    kmeans_model = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans_model.fit_predict(X_scaled)
    
    # Add cluster labels to original data
    df_clustered = df.iloc[X.index].copy()
    df_clustered['cluster'] = cluster_labels
    
    # Analyze clusters
    cluster_analysis = {}
    for cluster_id in range(optimal_k):
        cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]
        
        cluster_analysis[cluster_id] = {
            'size': len(cluster_data),
            'avg_spend': cluster_data['spend'].mean(),
            'avg_ctr': cluster_data['ctr'].mean(),
            'avg_cpa': cluster_data['cpa'].mean(),
            'avg_engagement': cluster_data['engagement_rate'].mean(),
            'platforms': cluster_data['platform'].value_counts().to_dict(),
            'characteristics': get_cluster_characteristics(cluster_data)
        }
    
    # PCA for visualization (if we have enough features)
    if X_scaled.shape[1] > 2:
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
    else:
        pca = None
        X_pca = X_scaled
    
    # Save models and analysis
    kmeans_data = {
        'model': kmeans_model,
        'scaler': scaler,
        'encoders': encoders,
        'pca': pca,
        'cluster_analysis': cluster_analysis,
        'df_clustered': df_clustered,
        'X_pca': X_pca,
        'feature_names': X.columns.tolist(),
        'optimal_k': optimal_k
    }
    
    with open('ml/kmeans_models.pkl', 'wb') as f:
        pickle.dump(kmeans_data, f)
    
    print(f"KMeans model saved to ml/kmeans_models.pkl")
    print(f"Optimal clusters: {optimal_k}")
    
    # Print cluster summary
    for cluster_id, analysis in cluster_analysis.items():
        print(f"\nCluster {cluster_id}:")
        print(f"  Size: {analysis['size']} campaigns")
        print(f"  Avg Spend: ${analysis['avg_spend']:.2f}")
        print(f"  Avg CTR: {analysis['avg_ctr']:.4f}")
        print(f"  Avg CPA: ${analysis['avg_cpa']:.2f}")
        print(f"  Characteristics: {analysis['characteristics']}")
    
    return kmeans_data

def get_cluster_characteristics(cluster_data):
    """Get human-readable characteristics of a cluster."""
    characteristics = []
    
    # High/Low spend
    if cluster_data['spend'].mean() > cluster_data['spend'].quantile(0.75):
        characteristics.append("High Spenders")
    elif cluster_data['spend'].mean() < cluster_data['spend'].quantile(0.25):
        characteristics.append("Low Spenders")
    
    # High/Low CTR
    if cluster_data['ctr'].mean() > cluster_data['ctr'].quantile(0.75):
        characteristics.append("High CTR")
    elif cluster_data['ctr'].mean() < cluster_data['ctr'].quantile(0.25):
        characteristics.append("Low CTR")
    
    # Platform preference
    top_platform = cluster_data['platform'].mode().iloc[0] if len(cluster_data) > 0 else "Unknown"
    characteristics.append(f"{top_platform} Focused")
    
    return ", ".join(characteristics)

def predict_cluster(new_data):
    """Predict cluster for new campaign data."""
    try:
        with open('ml/kmeans_models.pkl', 'rb') as f:
            kmeans_data = pickle.load(f)
        
        # Preprocess new data
        features = kmeans_data['feature_names']
        X_new = new_data[features].copy()
        
        # Encode categorical variables
        if 'demographic' in X_new.columns and 'demographic' in kmeans_data['encoders']:
            le = kmeans_data['encoders']['demographic']
            X_new['demographic_encoded'] = le.transform(X_new['demographic'].fillna('Unknown'))
            X_new = X_new.drop('demographic', axis=1)
        
        # Scale features
        X_new_scaled = kmeans_data['scaler'].transform(X_new)
        
        # Predict cluster
        cluster = kmeans_data['model'].predict(X_new_scaled)[0]
        
        return cluster, kmeans_data['cluster_analysis'][cluster]
    
    except FileNotFoundError:
        print("KMeans models not found. Run train_kmeans_models() first.")
        return None, None

if __name__ == "__main__":
    train_kmeans_models() 