"""
XGBoost Training - Enhanced Dataset with Feature Engineering
============================================================

Train XGBoost classifier on the enhanced dataset that includes:
- Interaction feature (TotalSF × OverallQual)
- Log-transformed features (TotalSF_log, LotArea_log)
- Refined class boundaries
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, confusion_matrix,
                            classification_report, precision_recall_fscore_support)
import json

print("=" * 80)
print("XGBOOST - ENHANCED DATASET")
print("=" * 80)
print()

# Load enhanced dataset
print("Loading enhanced dataset with feature engineering...")
df = pd.read_csv('../../data/processed_data_classification_fe.csv')
print(f"✓ Loaded: {df.shape[0]} samples, {df.shape[1]} features")
print()

# Separate features and target
X = df.drop(['price_class', 'SalePrice'], axis=1)
y = df['price_class']

# Get feature names before imputation
feature_names = X.columns.tolist()

print(f"Features: {X.shape[1]}")
print(f"Target distribution:")
print(y.value_counts().sort_index())
print()

# Handle missing values
print("Handling missing values with median imputation...")
imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)
print(f"✓ Imputation complete")
print()

# Train/test split (stratified)
print("Splitting data (80/20, stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train: {X_train.shape[0]} samples")
print(f"✓ Test: {X_test.shape[0]} samples")
print()

# Train XGBoost (no scaling needed)
print("Training XGBoost...")
print("Configuration:")
print("  - n_estimators: 100")
print("  - max_depth: 6")
print("  - learning_rate: 0.3")
print("  - random_state: 42")
print("  - eval_metric: mlogloss")
print()

model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.3,
    random_state=42,
    eval_metric='mlogloss',
    use_label_encoder=False
)
model.fit(X_train, y_train)
print("✓ Training complete")
print()

# Predictions
print("Generating predictions...")
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)
print("✓ Predictions complete")
print()

# Evaluate on training set
train_accuracy = accuracy_score(y_train, y_train_pred)
train_f1_macro = f1_score(y_train, y_train_pred, average='macro')

# Evaluate on test set
test_accuracy = accuracy_score(y_test, y_test_pred)
test_f1_macro = f1_score(y_test, y_test_pred, average='macro')
conf_matrix = confusion_matrix(y_test, y_test_pred)

# Per-class metrics
precision, recall, f1_class, support = precision_recall_fscore_support(
    y_test, y_test_pred, average=None
)

# Feature importance
feature_importance = model.feature_importances_
feature_importance_dict = [
    {'feature': feature_names[i], 'importance': float(imp)}
    for i, imp in enumerate(feature_importance)
]
feature_importance_dict.sort(key=lambda x: x['importance'], reverse=True)
top_15_features = feature_importance_dict[:15]

print("=" * 80)
print("RESULTS")
print("=" * 80)
print()

print("TRAINING SET:")
print(f"  Accuracy:  {train_accuracy:.4f}")
print(f"  F1-Macro:  {train_f1_macro:.4f}")
print()

print("TEST SET:")
print(f"  Accuracy:  {test_accuracy:.4f}")
print(f"  F1-Macro:  {test_f1_macro:.4f} ⭐ (Primary Metric)")
print()

print("PER-CLASS F1 SCORES (Test):")
for i, f1 in enumerate(f1_class):
    print(f"  Class {i}: {f1:.4f}")
print()

print("CONFUSION MATRIX (Test):")
print(conf_matrix)
print()

print("DETAILED CLASSIFICATION REPORT:")
print(classification_report(y_test, y_test_pred, 
                          target_names=['Class 0', 'Class 1', 'Class 2']))
print()

print("TOP 15 MOST IMPORTANT FEATURES:")
for i, feat in enumerate(top_15_features, 1):
    marker = " ⭐ NEW!" if feat['feature'] in ['TotalSF_x_OverallQual', 'TotalSF_log', 'LotArea_log'] else ""
    print(f"  {i:2d}. {feat['feature']:30s} {feat['importance']:.6f}{marker}")
print()

# Save results
results = {
    'model': 'XGBoost (Enhanced)',
    'dataset': 'processed_data_classification_fe.csv',
    'features': int(X.shape[1]),
    'train_accuracy': float(train_accuracy),
    'train_f1_macro': float(train_f1_macro),
    'test_accuracy': float(test_accuracy),
    'test_f1_macro': float(test_f1_macro),
    'confusion_matrix': conf_matrix.tolist(),
    'f1_per_class': f1_class.tolist(),
    'precision_per_class': precision.tolist(),
    'recall_per_class': recall.tolist(),
    'top_features': top_15_features
}

with open('../results/xgboost_results_enhanced.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✓ Results saved to: xgboost_results_enhanced.json")
print()

print("=" * 80)
print("XGBOOST TRAINING COMPLETE")
print("=" * 80)
print()
print(f"Test Accuracy: {test_accuracy:.4f}")
print(f"Test F1-Macro: {test_f1_macro:.4f} ⭐")
print("=" * 80)
