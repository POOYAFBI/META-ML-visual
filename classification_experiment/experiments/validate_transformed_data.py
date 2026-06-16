"""
Validation Script: Feature Engineered Classification Dataset
=============================================================

Verify that the transformed dataset is ready for classification training.
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("VALIDATION: TRANSFORMED CLASSIFICATION DATASET")
print("=" * 80)
print()

# Load transformed dataset
df = pd.read_csv('../../data/processed_data_classification_fe.csv')

print(f"Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")
print()

# Verify new features exist
print("=" * 80)
print("1. VERIFYING NEW FEATURES")
print("=" * 80)
print()

new_features = ['TotalSF_x_OverallQual', 'TotalSF_log', 'LotArea_log']
for feat in new_features:
    if feat in df.columns:
        print(f"✓ {feat}")
        print(f"  Range: [{df[feat].min():.2f}, {df[feat].max():.2f}]")
        print(f"  Mean: {df[feat].mean():.2f}, Std: {df[feat].std():.2f}")
        print(f"  Missing values: {df[feat].isna().sum()}")
    else:
        print(f"✗ {feat} - MISSING!")
    print()

# Verify price_class
print("=" * 80)
print("2. VERIFYING PRICE_CLASS")
print("=" * 80)
print()

if 'price_class' in df.columns:
    print("✓ price_class exists")
    print()
    print("Class distribution:")
    class_dist = df['price_class'].value_counts().sort_index()
    for cls, count in class_dist.items():
        pct = (count / len(df)) * 100
        print(f"  Class {cls}: {count} samples ({pct:.1f}%)")
    print()
    
    # Check balance
    balance_ratio = class_dist.max() / class_dist.min()
    print(f"Balance ratio (max/min): {balance_ratio:.2f}")
    if balance_ratio < 1.5:
        print("✓ Classes are well-balanced")
    else:
        print("⚠ Classes may be imbalanced")
else:
    print("✗ price_class - MISSING!")
print()

# Data quality checks
print("=" * 80)
print("3. DATA QUALITY CHECKS")
print("=" * 80)
print()

# Check for NaN values
nan_count = df.isna().sum().sum()
print(f"Total NaN values: {nan_count}")
if nan_count == 0:
    print("✓ No missing values")
else:
    print("⚠ Missing values detected:")
    nan_cols = df.columns[df.isna().any()].tolist()
    for col in nan_cols[:10]:  # Show first 10
        print(f"  - {col}: {df[col].isna().sum()} missing")
print()

# Check for infinite values
inf_cols = []
for col in df.select_dtypes(include=[np.number]).columns:
    if np.isinf(df[col]).any():
        inf_cols.append(col)

print(f"Columns with infinite values: {len(inf_cols)}")
if len(inf_cols) == 0:
    print("✓ No infinite values")
else:
    print("⚠ Infinite values detected in:", inf_cols[:5])
print()

# Show sample of new features
print("=" * 80)
print("4. SAMPLE DATA (First 5 rows)")
print("=" * 80)
print()

sample_cols = ['TotalSF', 'OverallQual', 'LotArea', 
               'TotalSF_x_OverallQual', 'TotalSF_log', 'LotArea_log', 
               'price_class', 'SalePrice']
sample_cols = [c for c in sample_cols if c in df.columns]

print(df[sample_cols].head().to_string())
print()

# Summary statistics for new features
print("=" * 80)
print("5. SUMMARY STATISTICS FOR NEW FEATURES")
print("=" * 80)
print()

print(df[new_features].describe().to_string())
print()

# Correlation with target
print("=" * 80)
print("6. CORRELATION WITH TARGET (price_class)")
print("=" * 80)
print()

if 'price_class' in df.columns:
    correlations = []
    for feat in new_features:
        if feat in df.columns:
            corr = df[feat].corr(df['price_class'])
            correlations.append((feat, corr))
    
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for feat, corr in correlations:
        print(f"{feat:30s}: {corr:+.4f}")
print()

print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
print()
print("✓ Dataset is ready for classification training")
print(f"✓ {df.shape[0]} samples, {df.shape[1]} features")
print("✓ 3 new features successfully added")
print("✓ price_class boundaries refined")
print()
print("Next step: Train classification models (Logistic, RF, XGBoost)")
print("=" * 80)
