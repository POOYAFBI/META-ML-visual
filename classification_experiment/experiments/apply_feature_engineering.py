"""
Feature Engineering for Classification Experiment
==================================================

This script applies three controlled feature transformations to Dataset A:
1. Interaction Feature: TotalSF × OverallQual
2. Log Transformations: log(1 + TotalSF) and log(1 + LotArea)
3. Class Boundary Cleanup: Refine price_class boundaries using quantile-based logic

Purpose: Evaluate impact of feature engineering on classification performance,
         especially for XGBoost.
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("CLASSIFICATION DATASET - FEATURE ENGINEERING")
print("=" * 80)
print()

# Load processed classification dataset
print("Loading processed classification dataset...")
df = pd.read_csv('../../data/processed_data.csv')
print(f"✓ Loaded dataset: {df.shape[0]} samples, {df.shape[1]} features")
print()

# Verify required features exist
required_features = ['TotalSF', 'OverallQual', 'LotArea', 'price_class', 'SalePrice']
missing = [f for f in required_features if f not in df.columns]
if missing:
    print(f"❌ ERROR: Missing required features: {missing}")
    exit(1)
print(f"✓ All required features present")
print()

# Display current class distribution
print("Current price_class distribution:")
print(df['price_class'].value_counts().sort_index())
print()

print("=" * 80)
print("TRANSFORMATION 1: INTERACTION FEATURE")
print("=" * 80)
print("Creating: TotalSF_x_OverallQual = TotalSF × OverallQual")
print()

# Create interaction feature
df['TotalSF_x_OverallQual'] = df['TotalSF'] * df['OverallQual']

print(f"✓ Created interaction feature")
print(f"  Min: {df['TotalSF_x_OverallQual'].min():.2f}")
print(f"  Max: {df['TotalSF_x_OverallQual'].max():.2f}")
print(f"  Mean: {df['TotalSF_x_OverallQual'].mean():.2f}")
print(f"  Median: {df['TotalSF_x_OverallQual'].median():.2f}")
print()

print("=" * 80)
print("TRANSFORMATION 2: LOG TRANSFORMATIONS")
print("=" * 80)
print("Applying log(1 + x) to reduce skewness")
print()

# Log transform TotalSF
print("2a. Log transform TotalSF:")
print(f"  Original - Min: {df['TotalSF'].min():.2f}, Max: {df['TotalSF'].max():.2f}, Mean: {df['TotalSF'].mean():.2f}")
df['TotalSF_log'] = np.log1p(df['TotalSF'])
print(f"  Transformed - Min: {df['TotalSF_log'].min():.2f}, Max: {df['TotalSF_log'].max():.2f}, Mean: {df['TotalSF_log'].mean():.2f}")
print(f"  ✓ Created TotalSF_log")
print()

# Log transform LotArea
print("2b. Log transform LotArea:")
print(f"  Original - Min: {df['LotArea'].min():.2f}, Max: {df['LotArea'].max():.2f}, Mean: {df['LotArea'].mean():.2f}")
df['LotArea_log'] = np.log1p(df['LotArea'])
print(f"  Transformed - Min: {df['LotArea_log'].min():.2f}, Max: {df['LotArea_log'].max():.2f}, Mean: {df['LotArea_log'].mean():.2f}")
print(f"  ✓ Created LotArea_log")
print()

print("=" * 80)
print("TRANSFORMATION 3: CLASS BOUNDARY CLEANUP")
print("=" * 80)
print("Refining price_class boundaries using quantile-based logic")
print()

# Analyze current class boundaries
print("Current class boundaries (based on SalePrice):")
for cls in sorted(df['price_class'].unique()):
    cls_data = df[df['price_class'] == cls]['SalePrice']
    print(f"  Class {cls}: ${cls_data.min():,} - ${cls_data.max():,} (n={len(cls_data)})")
print()

# Check for extreme outliers in SalePrice
print("Detecting extreme outliers...")
Q1 = df['SalePrice'].quantile(0.25)
Q3 = df['SalePrice'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 3 * IQR  # 3 IQR for extreme outliers
upper_bound = Q3 + 3 * IQR

extreme_low = df[df['SalePrice'] < lower_bound]
extreme_high = df[df['SalePrice'] > upper_bound]

print(f"  IQR: ${IQR:,.2f}")
print(f"  Extreme outlier bounds: ${lower_bound:,.2f} - ${upper_bound:,.2f}")
print(f"  Extreme low outliers: {len(extreme_low)} samples")
print(f"  Extreme high outliers: {len(extreme_high)} samples")
print()

# Refine class boundaries using quantile-based approach
print("Refining class boundaries using 33rd and 67th percentiles...")
p33 = df['SalePrice'].quantile(0.33)
p67 = df['SalePrice'].quantile(0.67)

print(f"  33rd percentile: ${p33:,.2f}")
print(f"  67th percentile: ${p67:,.2f}")
print()

# Create refined price_class
df['price_class_refined'] = pd.cut(
    df['SalePrice'],
    bins=[0, p33, p67, float('inf')],
    labels=[0, 1, 2],
    include_lowest=True
)
df['price_class_refined'] = df['price_class_refined'].astype(int)

# Compare original vs refined
print("Comparison: Original vs Refined class distribution:")
print("\nOriginal:")
print(df['price_class'].value_counts().sort_index())
print("\nRefined:")
print(df['price_class_refined'].value_counts().sort_index())
print()

# Calculate how many samples changed class
changes = (df['price_class'] != df['price_class_refined']).sum()
change_pct = (changes / len(df)) * 100
print(f"Number of samples that changed class: {changes} ({change_pct:.2f}%)")
print()

# Replace original price_class with refined version
df['price_class'] = df['price_class_refined']
df = df.drop('price_class_refined', axis=1)
print("✓ Replaced price_class with refined boundaries")
print()

print("=" * 80)
print("SUMMARY OF APPLIED TRANSFORMATIONS")
print("=" * 80)
print()
print("New features added:")
print("  1. TotalSF_x_OverallQual - Interaction between total square footage and quality")
print("  2. TotalSF_log - Log-transformed total square footage")
print("  3. LotArea_log - Log-transformed lot area")
print()
print("Modified features:")
print("  1. price_class - Refined using quantile-based boundaries")
print()
print(f"Final dataset shape: {df.shape[0]} samples, {df.shape[1]} features")
print()

# Save transformed dataset
output_file = '../../data/processed_data_classification_fe.csv'
df.to_csv(output_file, index=False)
print(f"✓ Saved transformed dataset to: {output_file}")
print()

# Generate feature list
new_features = ['TotalSF_x_OverallQual', 'TotalSF_log', 'LotArea_log']
with open('../results/new_features.txt', 'w') as f:
    f.write("NEW FEATURES ADDED FOR CLASSIFICATION\n")
    f.write("=" * 50 + "\n\n")
    for i, feat in enumerate(new_features, 1):
        f.write(f"{i}. {feat}\n")
    f.write(f"\nTotal new features: {len(new_features)}\n")
    f.write(f"Total features in dataset: {df.shape[1]}\n")
print("✓ Saved feature list to: new_features.txt")
print()

# Generate transformation summary report
with open('../reports/TRANSFORMATION_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write("# Feature Engineering Transformation Summary\n\n")
    f.write("**Date:** June 13, 2026\n")
    f.write("**Purpose:** Prepare classification dataset for model training experiments\n\n")
    f.write("---\n\n")
    
    f.write("## Applied Transformations\n\n")
    f.write("### 1. Interaction Feature\n\n")
    f.write("**Feature:** `TotalSF_x_OverallQual`\n")
    f.write("**Formula:** TotalSF × OverallQual\n")
    f.write("**Rationale:** Capture interaction between house size and quality\n\n")
    f.write(f"- Min: {df['TotalSF_x_OverallQual'].min():.2f}\n")
    f.write(f"- Max: {df['TotalSF_x_OverallQual'].max():.2f}\n")
    f.write(f"- Mean: {df['TotalSF_x_OverallQual'].mean():.2f}\n\n")
    
    f.write("### 2. Log Transformations\n\n")
    f.write("**Features:** `TotalSF_log`, `LotArea_log`\n")
    f.write("**Formula:** log(1 + x)\n")
    f.write("**Rationale:** Reduce skewness, normalize distributions\n\n")
    f.write("**TotalSF_log:**\n")
    f.write(f"- Min: {df['TotalSF_log'].min():.2f}\n")
    f.write(f"- Max: {df['TotalSF_log'].max():.2f}\n")
    f.write(f"- Mean: {df['TotalSF_log'].mean():.2f}\n\n")
    f.write("**LotArea_log:**\n")
    f.write(f"- Min: {df['LotArea_log'].min():.2f}\n")
    f.write(f"- Max: {df['LotArea_log'].max():.2f}\n")
    f.write(f"- Mean: {df['LotArea_log'].mean():.2f}\n\n")
    
    f.write("### 3. Class Boundary Cleanup\n\n")
    f.write("**Feature:** `price_class`\n")
    f.write("**Method:** Quantile-based boundaries (33rd and 67th percentiles)\n")
    f.write("**Rationale:** Ensure balanced classes and consistent boundary logic\n\n")
    f.write(f"- 33rd percentile: ${p33:,.2f}\n")
    f.write(f"- 67th percentile: ${p67:,.2f}\n")
    f.write(f"- Samples changed: {changes} ({change_pct:.2f}%)\n\n")
    
    f.write("## Dataset Summary\n\n")
    f.write(f"- **Total samples:** {df.shape[0]}\n")
    f.write(f"- **Total features:** {df.shape[1]}\n")
    f.write(f"- **New features added:** {len(new_features)}\n\n")
    
    f.write("**Class distribution (after refinement):**\n\n")
    for cls in sorted(df['price_class'].unique()):
        count = (df['price_class'] == cls).sum()
        pct = (count / len(df)) * 100
        f.write(f"- Class {cls}: {count} samples ({pct:.1f}%)\n")
    f.write("\n")
    
    f.write("## Output Files\n\n")
    f.write("1. `processed_data_classification_fe.csv` - Transformed dataset\n")
    f.write("2. `new_features.txt` - List of new features\n")
    f.write("3. `TRANSFORMATION_SUMMARY.md` - This document\n\n")
    
    f.write("---\n\n")
    f.write("## Next Steps\n\n")
    f.write("1. Train classification models (Logistic Regression, Random Forest, XGBoost)\n")
    f.write("2. Evaluate performance on transformed dataset\n")
    f.write("3. Compare with baseline results (without feature engineering)\n")
    f.write("4. Analyze impact of each transformation\n\n")
    
    f.write("**Dataset is ready for classification training experiments!** ✓\n")

print("✓ Saved transformation summary to: TRANSFORMATION_SUMMARY.md")
print()

print("=" * 80)
print("FEATURE ENGINEERING COMPLETE ✓")
print("=" * 80)
print()
print("✓ All transformations applied successfully")
print("✓ Dataset ready for classification training")
print("✓ Output files generated")
print()
print("Next Phase: Train classification models on transformed data")
print("=" * 80)
