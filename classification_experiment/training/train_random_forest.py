"""
Random Forest Classifier - Classification Experiment
=====================================================
Model: Random Forest (Tree-based ensemble)
Target: price_class (0=low, 1=medium, 2=high)
Dataset: Dataset A (processed_data.csv)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, 
    f1_score, 
    classification_report, 
    confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
RANDOM_STATE = 42

print("=" * 70)
print("RANDOM FOREST CLASSIFIER - CLASSIFICATION EXPERIMENT")
print("=" * 70)
print()

# Load dataset
print("[1/5] Loading Dataset A...")
df = pd.read_csv('../../data/processed_data.csv')
print(f"   Dataset shape: {df.shape}")
print(f"   Total samples: {len(df)}")

# Separate features and targets
X = df.drop(['SalePrice', 'price_class'], axis=1)
y = df['price_class']

# Handle missing values (fill with median)
nan_count = X.isna().sum().sum()
if nan_count > 0:
    print(f"   ⚠️  Found {nan_count} NaN values - filling with column medians")
    X = X.fillna(X.median())

print(f"   Features: {X.shape[1]}")
print(f"   Target: price_class")
print()

# Check class distribution
print("[2/5] Target Distribution:")
class_dist = y.value_counts().sort_index()
for cls, count in class_dist.items():
    class_name = ['low', 'medium', 'high'][cls]
    print(f"   Class {cls} ({class_name}): {count} samples ({count/len(y)*100:.1f}%)")
print()

# Train-test split
print("[3/5] Creating train-test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"   Training samples: {len(X_train)}")
print(f"   Test samples: {len(X_test)}")
print()

# Train model (no scaling needed for tree-based models)
print("[4/5] Training Random Forest Classifier...")
print("   Hyperparameters:")
print("     - Number of trees: 100")
print("     - Max depth: None (unlimited)")
print("     - Min samples split: 2")
print("     - Random state: 42")
print()

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    random_state=RANDOM_STATE,
    n_jobs=-1  # Use all CPU cores
)

model.fit(X_train, y_train)
print("   ✓ Model training complete")
print()

# Evaluate model
print("[5/5] Model Evaluation")
print("-" * 70)

# Predictions
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Training metrics
train_accuracy = accuracy_score(y_train, y_train_pred)
train_f1_macro = f1_score(y_train, y_train_pred, average='macro')

print(f"\n{'TRAINING SET PERFORMANCE':^70}")
print("-" * 70)
print(f"   Accuracy:       {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
print(f"   F1-Score (macro): {train_f1_macro:.4f}")
print()

# Test metrics
test_accuracy = accuracy_score(y_test, y_test_pred)
test_f1_macro = f1_score(y_test, y_test_pred, average='macro')

print(f"\n{'TEST SET PERFORMANCE (PRIMARY METRICS)':^70}")
print("=" * 70)
print(f"   Accuracy:       {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
print(f"   F1-Score (macro): {test_f1_macro:.4f} ⭐ PRIMARY METRIC")
print("=" * 70)
print()

# Check for overfitting
print("\nOVERFITTING ANALYSIS:")
print("-" * 70)
acc_gap = train_accuracy - test_accuracy
f1_gap = train_f1_macro - test_f1_macro
print(f"   Accuracy gap (train - test): {acc_gap:.4f} ({acc_gap*100:.2f}%)")
print(f"   F1-macro gap (train - test): {f1_gap:.4f}")
if acc_gap > 0.10:
    print("   ⚠️  Warning: Significant overfitting detected")
elif acc_gap > 0.05:
    print("   ⚠️  Moderate overfitting detected")
else:
    print("   ✓ Good generalization")
print()

# Detailed classification report
print("\nDETAILED CLASSIFICATION REPORT (Test Set):")
print("-" * 70)
print(classification_report(
    y_test, 
    y_test_pred, 
    target_names=['Low', 'Medium', 'High'],
    digits=4
))

# Confusion matrix
print("\nCONFUSION MATRIX (Test Set):")
print("-" * 70)
cm = confusion_matrix(y_test, y_test_pred)
print("\n                Predicted")
print("              Low  Medium  High")
print(f"Actual  Low    {cm[0,0]:3d}    {cm[0,1]:3d}   {cm[0,2]:3d}")
print(f"       Medium  {cm[1,0]:3d}    {cm[1,1]:3d}   {cm[1,2]:3d}")
print(f"       High    {cm[2,0]:3d}    {cm[2,1]:3d}   {cm[2,2]:3d}")
print()

# Per-class F1 scores
f1_per_class = f1_score(y_test, y_test_pred, average=None)
print("\nPER-CLASS F1-SCORES (Test Set):")
print("-" * 70)
for i, (cls_name, f1) in enumerate(zip(['Low', 'Medium', 'High'], f1_per_class)):
    print(f"   {cls_name:8s}: {f1:.4f}")
print(f"   {'Macro Avg':8s}: {test_f1_macro:.4f}")
print()

# Feature importance (top 15)
print("\nTOP 15 FEATURE IMPORTANCES:")
print("-" * 70)
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(15).iterrows():
    print(f"   {row['feature']:30s}: {row['importance']:.4f}")
print()

# Model characteristics
print("\nMODEL CHARACTERISTICS:")
print("-" * 70)
print(f"   Model Type: Random Forest (Bagging Ensemble)")
print(f"   Decision Boundary: Non-linear (ensemble of trees)")
print(f"   Number of trees: {model.n_estimators}")
print(f"   Number of classes: 3")
print(f"   Number of features: {X.shape[1]}")
print(f"   Scaling applied: No (not needed for trees)")
print()

# Save results
results = {
    'model': 'Random Forest',
    'train_accuracy': train_accuracy,
    'train_f1_macro': train_f1_macro,
    'test_accuracy': test_accuracy,
    'test_f1_macro': test_f1_macro,
    'confusion_matrix': cm.tolist(),
    'f1_per_class': f1_per_class.tolist(),
    'top_features': feature_importance.head(15).to_dict('records')
}

import json
with open('../results/random_forest_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✓ Results saved to: random_forest_results.json")
print()
print("=" * 70)
print("RANDOM FOREST TRAINING COMPLETE")
print("=" * 70)
