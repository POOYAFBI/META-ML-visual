"""
Feature Engineering Audit and Minimal FE Dataset Creation
==========================================================
This script audits all features in processed_data.csv and creates a new dataset
with minimal feature engineering for controlled experimentation.

Purpose: Measure the impact of Feature Engineering on different ML models
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("FEATURE ENGINEERING AUDIT")
print("=" * 80)

# Load processed dataset
df = pd.read_csv('../data/processed_data.csv')
print(f"\n✓ Loaded processed_data.csv")
print(f"  Shape: {df.shape}")

# Get all feature names (excluding targets)
all_features = [col for col in df.columns if col not in ['SalePrice', 'price_class']]
print(f"\n✓ Total features to audit: {len(all_features)}")

# ============================================================================
# FEATURE CATEGORIZATION
# ============================================================================

# Category A: Raw numerical features from original dataset
raw_numerical_features = [
    'MSSubClass', 'LotFrontage', 'LotArea', 'OverallQual', 'OverallCond',
    'YearBuilt', 'YearRemodAdd', 'MasVnrArea', 'BsmtFinSF1', 'BsmtFinSF2',
    'BsmtUnfSF', 'TotalBsmtSF', '1stFlrSF', '2ndFlrSF', 'LowQualFinSF',
    'GrLivArea', 'BsmtFullBath', 'BsmtHalfBath', 'FullBath', 'HalfBath',
    'BedroomAbvGr', 'KitchenAbvGr', 'TotRmsAbvGrd', 'Fireplaces',
    'GarageYrBlt', 'GarageCars', 'GarageArea', 'WoodDeckSF', 'OpenPorchSF',
    'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea', 'MiscVal',
    'MoSold', 'YrSold'
]

# Category B: Engineered features (TO BE REMOVED)
engineered_features = {
    'TotalSF': 'Aggregation: TotalBsmtSF + 1stFlrSF + 2ndFlrSF',
    'HouseAge': 'Derived metric: 2024 - YearBuilt',
    'YearsSinceRemod': 'Derived metric: 2024 - YearRemodAdd',
    'TotalBathrooms': 'Aggregation: FullBath + 0.5*HalfBath + BsmtFullBath + 0.5*BsmtHalfBath',
    'OverallScore': 'Composite indicator: OverallQual × OverallCond',
    'TotalPorchSF': 'Aggregation: OpenPorchSF + EnclosedPorch + 3SsnPorch + ScreenPorch',
    'HasGarage': 'Binary indicator: derived from GarageArea',
    'HasBasement': 'Binary indicator: derived from TotalBsmtSF',
    'HasFireplace': 'Binary indicator: derived from Fireplaces',
    'IsRemodeled': 'Binary indicator: derived from YearBuilt vs YearRemodAdd'
}

# Category C: Encoded categorical features (KEEP)
# These are transformations of original categorical data, not engineered features
encoded_ordinal_features = [
    'ExterQual_encoded', 'ExterCond_encoded', 'BsmtQual_encoded', 
    'BsmtCond_encoded', 'BsmtExposure_encoded', 'BsmtFinType1_encoded', 
    'BsmtFinType2_encoded', 'HeatingQC_encoded', 'KitchenQual_encoded', 
    'FireplaceQu_encoded', 'GarageQual_encoded', 'GarageCond_encoded'
]

# One-hot encoded features (all features with underscores that aren't ordinal)
one_hot_encoded_features = [
    col for col in all_features 
    if '_' in col and col not in encoded_ordinal_features and col not in engineered_features
]

# ============================================================================
# AUDIT REPORT GENERATION
# ============================================================================

print("\n" + "=" * 80)
print("FEATURE AUDIT RESULTS")
print("=" * 80)

# Features to KEEP
features_to_keep = []

print("\n--- CATEGORY A: Raw Numerical Features (KEEP) ---")
raw_present = [col for col in raw_numerical_features if col in df.columns]
print(f"Count: {len(raw_present)}")
for col in raw_present:
    print(f"  ✓ {col}")
    features_to_keep.append(col)

print("\n--- CATEGORY C: Encoded Ordinal Features (KEEP) ---")
print(f"Count: {len(encoded_ordinal_features)}")
for col in encoded_ordinal_features:
    if col in df.columns:
        print(f"  ✓ {col}")
        features_to_keep.append(col)

print("\n--- CATEGORY C: One-Hot Encoded Features (KEEP) ---")
print(f"Count: {len(one_hot_encoded_features)}")
print(f"  Examples: {one_hot_encoded_features[:5]}...")
print(f"  (Complete list available in audit report)")
features_to_keep.extend(one_hot_encoded_features)

# Features to REMOVE
print("\n--- CATEGORY B: Engineered Features (REMOVE) ---")
engineered_present = [col for col in engineered_features.keys() if col in df.columns]
print(f"Count: {len(engineered_present)}")
for col in engineered_present:
    print(f"  ✗ {col}: {engineered_features[col]}")

# ============================================================================
# CREATE MINIMAL FE DATASET
# ============================================================================

print("\n" + "=" * 80)
print("CREATING MINIMAL FE DATASET")
print("=" * 80)

# Select features to keep + targets
columns_to_keep = features_to_keep + ['SalePrice', 'price_class']
df_minimal = df[columns_to_keep].copy()

print(f"\n✓ Created minimal FE dataset")
print(f"  Original features: {len(all_features)}")
print(f"  Minimal FE features: {len(features_to_keep)}")
print(f"  Removed features: {len(engineered_present)}")
print(f"  Reduction: {len(engineered_present)} features ({len(engineered_present)/len(all_features)*100:.1f}%)")

# Save minimal FE dataset
df_minimal.to_csv('../data/processed_data_minimal_fe.csv', index=False)
print(f"\n✓ Saved: processed_data_minimal_fe.csv")
print(f"  Shape: {df_minimal.shape}")

# ============================================================================
# GENERATE DETAILED AUDIT REPORT
# ============================================================================

print("\n" + "=" * 80)
print("GENERATING AUDIT REPORT")
print("=" * 80)

report_lines = []
report_lines.append("# Feature Engineering Audit Report")
report_lines.append("")
report_lines.append("## Executive Summary")
report_lines.append("")
report_lines.append(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append(f"**Purpose:** Create controlled experiment to measure Feature Engineering impact on ML models")
report_lines.append("")
report_lines.append("### Dataset Comparison")
report_lines.append("")
report_lines.append("| Metric | Full FE Dataset | Minimal FE Dataset | Difference |")
report_lines.append("|--------|-----------------|-----------------------|------------|")
report_lines.append(f"| Total Features | {len(all_features)} | {len(features_to_keep)} | -{len(engineered_present)} ({-len(engineered_present)/len(all_features)*100:.1f}%) |")
report_lines.append(f"| Raw Features | {len(raw_present)} | {len(raw_present)} | 0 |")
report_lines.append(f"| Encoded Features | {len(encoded_ordinal_features) + len(one_hot_encoded_features)} | {len(encoded_ordinal_features) + len(one_hot_encoded_features)} | 0 |")
report_lines.append(f"| Engineered Features | {len(engineered_present)} | 0 | -{len(engineered_present)} |")
report_lines.append(f"| Samples | {df.shape[0]} | {df_minimal.shape[0]} | 0 |")
report_lines.append("")

report_lines.append("## Scientific Rationale")
report_lines.append("")
report_lines.append("### Experimental Design")
report_lines.append("")
report_lines.append("This audit creates two datasets for a controlled experiment:")
report_lines.append("")
report_lines.append("**Dataset A (Full FE):** `processed_data.csv`")
report_lines.append("- Contains all raw features, encoded features, AND engineered features")
report_lines.append(f"- Total: {len(all_features)} features")
report_lines.append("- Includes aggregations, ratios, composite indicators, derived metrics")
report_lines.append("")
report_lines.append("**Dataset B (Minimal FE):** `processed_data_minimal_fe.csv`")
report_lines.append("- Contains only raw features and encoded categorical variables")
report_lines.append(f"- Total: {len(features_to_keep)} features")
report_lines.append("- NO aggregations, ratios, composite indicators, or derived metrics")
report_lines.append("")

report_lines.append("### Research Hypothesis")
report_lines.append("")
report_lines.append("**Current Observation:**")
report_lines.append("- Linear Regression performs BEST on full FE dataset")
report_lines.append("- XGBoost performs SECOND")
report_lines.append("- Random Forest performs THIRD")
report_lines.append("")
report_lines.append("**Hypothesis:**")
report_lines.append("Extensive feature engineering may disproportionately benefit Linear Regression because:")
report_lines.append("1. Linear models cannot create non-linear interactions automatically")
report_lines.append("2. Engineered features provide explicit non-linear relationships")
report_lines.append("3. Tree-based models (RF, XGBoost) can discover these patterns naturally")
report_lines.append("")
report_lines.append("**Expected Results on Minimal FE Dataset:**")
report_lines.append("- Tree-based models (XGBoost, RF) should maintain or improve performance")
report_lines.append("- Linear Regression performance should decrease significantly")
report_lines.append("- This would confirm FE benefits Linear models disproportionately")
report_lines.append("")

report_lines.append("### Comparison Metrics")
report_lines.append("")
report_lines.append("For each model (Linear Regression, Random Forest, XGBoost), measure:")
report_lines.append("")
report_lines.append("1. **Regression Performance:**")
report_lines.append("   - Root Mean Squared Error (RMSE)")
report_lines.append("   - R² Score")
report_lines.append("   - Mean Absolute Error (MAE)")
report_lines.append("")
report_lines.append("2. **Classification Performance:**")
report_lines.append("   - Accuracy")
report_lines.append("   - Precision, Recall, F1-Score (per class)")
report_lines.append("")
report_lines.append("3. **Performance Delta:**")
report_lines.append("   - Calculate: `(Full_FE_Score - Minimal_FE_Score) / Full_FE_Score × 100%`")
report_lines.append("   - Shows percentage performance drop when FE removed")
report_lines.append("   - Higher delta = model benefited more from FE")
report_lines.append("")

report_lines.append("## Detailed Feature Categorization")
report_lines.append("")

# Category A
report_lines.append(f"### Category A: Raw Numerical Features (KEPT: {len(raw_present)})")
report_lines.append("")
report_lines.append("These are original features from the dataset with no transformations except missing value imputation.")
report_lines.append("")
report_lines.append("| Feature | Description |")
report_lines.append("|---------|-------------|")

feature_descriptions = {
    'MSSubClass': 'Type of dwelling',
    'LotFrontage': 'Linear feet of street connected to property',
    'LotArea': 'Lot size in square feet',
    'OverallQual': 'Overall material and finish quality (1-10)',
    'OverallCond': 'Overall condition rating (1-10)',
    'YearBuilt': 'Original construction year',
    'YearRemodAdd': 'Remodel year',
    'MasVnrArea': 'Masonry veneer area',
    'BsmtFinSF1': 'Type 1 finished basement area',
    'BsmtFinSF2': 'Type 2 finished basement area',
    'BsmtUnfSF': 'Unfinished basement area',
    'TotalBsmtSF': 'Total basement area',
    '1stFlrSF': 'First floor area',
    '2ndFlrSF': 'Second floor area',
    'LowQualFinSF': 'Low quality finished area',
    'GrLivArea': 'Above grade living area',
    'BsmtFullBath': 'Basement full bathrooms',
    'BsmtHalfBath': 'Basement half bathrooms',
    'FullBath': 'Full bathrooms above grade',
    'HalfBath': 'Half bathrooms above grade',
    'BedroomAbvGr': 'Bedrooms above grade',
    'KitchenAbvGr': 'Kitchens above grade',
    'TotRmsAbvGrd': 'Total rooms above grade',
    'Fireplaces': 'Number of fireplaces',
    'GarageYrBlt': 'Year garage built',
    'GarageCars': 'Garage capacity in cars',
    'GarageArea': 'Garage area in square feet',
    'WoodDeckSF': 'Wood deck area',
    'OpenPorchSF': 'Open porch area',
    'EnclosedPorch': 'Enclosed porch area',
    '3SsnPorch': 'Three season porch area',
    'ScreenPorch': 'Screen porch area',
    'PoolArea': 'Pool area',
    'MiscVal': 'Value of miscellaneous feature',
    'MoSold': 'Month sold',
    'YrSold': 'Year sold'
}

for col in raw_present:
    desc = feature_descriptions.get(col, 'Original feature')
    report_lines.append(f"| {col} | {desc} |")

report_lines.append("")

# Category C - Ordinal
report_lines.append(f"### Category C: Encoded Ordinal Features (KEPT: {len(encoded_ordinal_features)})")
report_lines.append("")
report_lines.append("These are label-encoded categorical features that have inherent ordering (e.g., quality ratings).")
report_lines.append("")
report_lines.append("| Feature | Original Feature | Encoding Type |")
report_lines.append("|---------|------------------|---------------|")

for col in encoded_ordinal_features:
    if col in df.columns:
        original = col.replace('_encoded', '')
        report_lines.append(f"| {col} | {original} | Label Encoding (ordinal) |")

report_lines.append("")

# Category C - One-Hot
report_lines.append(f"### Category C: One-Hot Encoded Features (KEPT: {len(one_hot_encoded_features)})")
report_lines.append("")
report_lines.append("These are one-hot encoded nominal categorical features (no inherent ordering).")
report_lines.append("")
report_lines.append("**Feature Prefixes and Counts:**")
report_lines.append("")

# Group by prefix
prefix_groups = {}
for col in one_hot_encoded_features:
    prefix = col.rsplit('_', 1)[0]
    if prefix not in prefix_groups:
        prefix_groups[prefix] = []
    prefix_groups[prefix].append(col)

report_lines.append("| Original Feature | Encoded Columns | Count |")
report_lines.append("|------------------|-----------------|-------|")
for prefix in sorted(prefix_groups.keys()):
    cols = prefix_groups[prefix]
    report_lines.append(f"| {prefix} | {', '.join(cols[:3])}{'...' if len(cols) > 3 else ''} | {len(cols)} |")

report_lines.append("")

# Category B - Engineered
report_lines.append(f"### Category B: Engineered Features (REMOVED: {len(engineered_present)})")
report_lines.append("")
report_lines.append("These features were created through feature engineering and are removed in the minimal FE dataset.")
report_lines.append("")
report_lines.append("| Feature | Type | Formula/Logic | Reason for Removal |")
report_lines.append("|---------|------|---------------|---------------------|")

feature_types = {
    'TotalSF': 'Aggregation',
    'HouseAge': 'Derived Metric',
    'YearsSinceRemod': 'Derived Metric',
    'TotalBathrooms': 'Aggregation',
    'OverallScore': 'Composite Indicator',
    'TotalPorchSF': 'Aggregation',
    'HasGarage': 'Binary Indicator',
    'HasBasement': 'Binary Indicator',
    'HasFireplace': 'Binary Indicator',
    'IsRemodeled': 'Binary Indicator'
}

removal_reasons = {
    'TotalSF': 'Combines multiple raw area features; tree models can learn this',
    'HouseAge': 'Derived from YearBuilt; linear transformation',
    'YearsSinceRemod': 'Derived from YearRemodAdd; linear transformation',
    'TotalBathrooms': 'Weighted sum of bathroom features; tree models can aggregate',
    'OverallScore': 'Product of quality and condition; interaction term',
    'TotalPorchSF': 'Sum of porch areas; tree models can aggregate',
    'HasGarage': 'Binary threshold on GarageArea; tree models can learn threshold',
    'HasBasement': 'Binary threshold on TotalBsmtSF; tree models can learn threshold',
    'HasFireplace': 'Binary threshold on Fireplaces; tree models can learn threshold',
    'IsRemodeled': 'Comparison of two year features; tree models can learn comparison'
}

for col in engineered_present:
    ftype = feature_types.get(col, 'Engineered')
    formula = engineered_features[col]
    reason = removal_reasons.get(col, 'Not a raw feature')
    report_lines.append(f"| {col} | {ftype} | {formula} | {reason} |")

report_lines.append("")

report_lines.append("## Impact Analysis Framework")
report_lines.append("")
report_lines.append("### Step 1: Train Models on Both Datasets")
report_lines.append("")
report_lines.append("Train each model on:")
report_lines.append("1. Full FE Dataset (`processed_data.csv`)")
report_lines.append("2. Minimal FE Dataset (`processed_data_minimal_fe.csv`)")
report_lines.append("")
report_lines.append("Models to test:")
report_lines.append("- Linear Regression")
report_lines.append("- Random Forest")
report_lines.append("- XGBoost")
report_lines.append("")

report_lines.append("### Step 2: Calculate Performance Metrics")
report_lines.append("")
report_lines.append("For each model and dataset combination, record:")
report_lines.append("")
report_lines.append("**Regression Task:**")
report_lines.append("- RMSE (lower is better)")
report_lines.append("- R² (higher is better)")
report_lines.append("- MAE (lower is better)")
report_lines.append("")
report_lines.append("**Classification Task:**")
report_lines.append("- Overall Accuracy")
report_lines.append("- Per-class Precision, Recall, F1")
report_lines.append("")

report_lines.append("### Step 3: Compute Feature Engineering Impact Score")
report_lines.append("")
report_lines.append("For each model, calculate:")
report_lines.append("")
report_lines.append("```")
report_lines.append("FE_Impact_Score = ((Metric_Full_FE - Metric_Minimal_FE) / Metric_Full_FE) × 100%")
report_lines.append("```")
report_lines.append("")
report_lines.append("**Interpretation:**")
report_lines.append("- **Positive score:** Model performs better with feature engineering")
report_lines.append("- **Negative score:** Model performs worse with feature engineering (rare)")
report_lines.append("- **Zero score:** No impact from feature engineering")
report_lines.append("- **Higher absolute value:** Greater dependence on feature engineering")
report_lines.append("")

report_lines.append("### Step 4: Comparative Analysis")
report_lines.append("")
report_lines.append("Compare FE Impact Scores across models to determine:")
report_lines.append("")
report_lines.append("1. **Which model benefits MOST from feature engineering?**")
report_lines.append("   - Expected: Linear Regression")
report_lines.append("")
report_lines.append("2. **Which model is MOST robust without feature engineering?**")
report_lines.append("   - Expected: XGBoost or Random Forest")
report_lines.append("")
report_lines.append("3. **Does model ranking change between datasets?**")
report_lines.append("   - Current on Full FE: Linear > XGBoost > Random Forest")
report_lines.append("   - Expected on Minimal FE: XGBoost > Random Forest > Linear")
report_lines.append("")

report_lines.append("## Expected Outcomes")
report_lines.append("")
report_lines.append("### Hypothesis Confirmation Criteria")
report_lines.append("")
report_lines.append("The hypothesis that \"Feature Engineering disproportionately benefits Linear Regression\" is confirmed if:")
report_lines.append("")
report_lines.append("1. **Linear Regression FE Impact Score > XGBoost FE Impact Score**")
report_lines.append("   - Linear model shows larger performance drop without FE")
report_lines.append("")
report_lines.append("2. **Linear Regression FE Impact Score > Random Forest FE Impact Score**")
report_lines.append("   - Linear model shows larger performance drop without FE")
report_lines.append("")
report_lines.append("3. **Model Ranking Changes**")
report_lines.append("   - Full FE: Linear #1")
report_lines.append("   - Minimal FE: Linear NOT #1 (falls to #2 or #3)")
report_lines.append("")

report_lines.append("### Alternative Outcomes")
report_lines.append("")
report_lines.append("**Scenario A: All models benefit equally**")
report_lines.append("- All FE Impact Scores similar")
report_lines.append("- Suggests: Feature engineering provides universal benefit")
report_lines.append("- Implication: Continue using full FE for all models")
report_lines.append("")
report_lines.append("**Scenario B: Tree models benefit more**")
report_lines.append("- XGBoost/RF Impact Scores > Linear Impact Score")
report_lines.append("- Suggests: Tree models also benefit from pre-computed features")
report_lines.append("- Implication: Feature engineering helps all models, not just linear")
report_lines.append("")
report_lines.append("**Scenario C: Hypothesis confirmed**")
report_lines.append("- Linear Impact Score >> Tree-based Impact Scores")
report_lines.append("- Suggests: Linear models need FE, tree models don't")
report_lines.append("- Implication: Can use simpler features for tree-based models in production")
report_lines.append("")

report_lines.append("## Next Steps")
report_lines.append("")
report_lines.append("1. [x] **COMPLETED:** Feature audit and minimal FE dataset creation")
report_lines.append("2. [ ] **TODO:** Train Linear Regression on `processed_data_minimal_fe.csv`")
report_lines.append("3. [ ] **TODO:** Train Random Forest on `processed_data_minimal_fe.csv`")
report_lines.append("4. [ ] **TODO:** Train XGBoost on `processed_data_minimal_fe.csv`")
report_lines.append("5. [ ] **TODO:** Compare results between full FE and minimal FE datasets")
report_lines.append("6. [ ] **TODO:** Generate comparative analysis report with FE Impact Scores")
report_lines.append("7. [ ] **TODO:** Draw conclusions about Feature Engineering impact per model")
report_lines.append("")

report_lines.append("## Files Generated")
report_lines.append("")
report_lines.append("| File | Description | Features |")
report_lines.append("|------|-------------|----------|")
report_lines.append(f"| `processed_data.csv` | Full FE dataset (existing) | {len(all_features)} |")
report_lines.append(f"| `processed_data_minimal_fe.csv` | Minimal FE dataset (new) | {len(features_to_keep)} |")
report_lines.append(f"| `FEATURE_ENGINEERING_AUDIT.md` | This audit report | - |")
report_lines.append("")

report_lines.append("## Conclusion")
report_lines.append("")
report_lines.append("This audit successfully identified and removed 10 engineered features from the processed dataset,")
report_lines.append("creating a controlled experimental setup to measure the impact of feature engineering on model performance.")
report_lines.append("")
report_lines.append("The minimal FE dataset preserves all raw information and categorical encodings while removing")
report_lines.append("aggregations, derived metrics, and composite indicators that might disproportionately benefit certain models.")
report_lines.append("")
report_lines.append("The experimental framework is now ready for model training and comparative analysis.")
report_lines.append("")

report_lines.append("---")
report_lines.append(f"*Generated on {pd.Timestamp.now().strftime('%Y-%m-%d at %H:%M:%S')}*")

# Save report
report_content = '\n'.join(report_lines)
with open('FEATURE_ENGINEERING_AUDIT.md', 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\n✓ Saved: FEATURE_ENGINEERING_AUDIT.md")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)

print(f"\n📊 Summary:")
print(f"  ✓ Total features audited: {len(all_features)}")
print(f"  ✓ Raw features kept: {len(raw_present)}")
print(f"  ✓ Encoded features kept: {len(encoded_ordinal_features) + len(one_hot_encoded_features)}")
print(f"  ✓ Engineered features removed: {len(engineered_present)}")
print(f"  ✓ Final minimal FE feature count: {len(features_to_keep)}")

print(f"\n📁 Files created:")
print(f"  ✓ processed_data_minimal_fe.csv ({df_minimal.shape[0]} rows × {df_minimal.shape[1]} cols)")
print(f"  ✓ FEATURE_ENGINEERING_AUDIT.md")

print(f"\n🎯 Next Steps:")
print(f"  1. Train models on processed_data_minimal_fe.csv")
print(f"  2. Compare performance with full FE results")
print(f"  3. Calculate FE Impact Scores")
print(f"  4. Determine which model benefits most from feature engineering")

print("\n" + "=" * 80)
