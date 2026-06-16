"""
Logistic Regression Classifier - Classification Experiment
============================================================
Model: Logistic Regression (Linear baseline for classification)
Target: price_class (0=low, 1=medium, 2=high)
Dataset: Dataset A (processed_data.csv)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
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
print("LOGISTIC REGRESSION CLASSIFIER - CLASSIFICATION EXPERIMENT")
print("=" * 70)
print()

# Load dataset
print("[1/6] Loading Dataset A...")
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
print("[2/6] Target Distribution:")
class_dist = y.value_counts().sort_index()
for cls, count in class_dist.items():
    class_name = ['low', 'medium', 'high'][cls]
    print(f"   Class {cls} ({class_name}): {count} samples ({count/len(y)*100:.1f}%)")
print()

# Train-test split
print("[3/6] Creating train-test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"   Training samples: {len(X_train)}")
print(f"   Test samples: {len(X_test)}")
print()

# Scale features (CRITICAL for Logistic Regression)
print("[4/6] Scaling features (StandardScaler)...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✓ Features scaled (mean=0, std=1)")
print()

# Train model
print("[5/6] Training Logistic Regression...")
print("   Hyperparameters:")
print("     - Solver: lbfgs")
print("     - Max iterations: 1000")
print("     - Random state: 42")
print()

model = LogisticRegression(
    solver='lbfgs',
    max_iter=1000,
    random_state=RANDOM_STATE
)

model.fit(X_train_scaled, y_train)
print("   ✓ Model training complete")
print()

# Evaluate model
print("[6/6] Model Evaluation")
print("-" * 70)

# Predictions
y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)

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

# Model characteristics
print("\nMODEL CHARACTERISTICS:")
print("-" * 70)
print(f"   Model Type: Logistic Regression (Linear Classifier)")
print(f"   Decision Boundary: Linear (hyperplanes)")
print(f"   Number of classes: 3")
print(f"   Number of features: {X.shape[1]}")
print(f"   Scaling applied: Yes (StandardScaler)")
print()

# Save results
results = {
    'model': 'Logistic Regression',
    'train_accuracy': train_accuracy,
    'train_f1_macro': train_f1_macro,
    'test_accuracy': test_accuracy,
    'test_f1_macro': test_f1_macro,
    'confusion_matrix': cm.tolist(),
    'f1_per_class': f1_per_class.tolist()
}

import json
with open('../results/logistic_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✓ Results saved to: logistic_results.json")
print()
print("=" * 70)
print("LOGISTIC REGRESSION TRAINING COMPLETE")
print("=" * 70)
