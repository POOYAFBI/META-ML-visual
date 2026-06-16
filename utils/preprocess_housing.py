"""
Ames Housing Dataset Preprocessing Pipeline
============================================
This script performs comprehensive data cleaning, preprocessing, and feature engineering
for the Ames Housing dataset to prepare it for multi-task ML (regression and classification).

Author: Senior ML Engineer
Purpose: Teaching document for beginner ML engineers
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# STEP 1: DATA LOADING AND INITIAL INSPECTION
# ============================================================================
print("=" * 80)
print("STEP 1: DATA LOADING AND INITIAL INSPECTION")
print("=" * 80)

# Load the dataset
df = pd.read_csv('../data/train.csv')
print(f"\n✓ Dataset loaded successfully!")
print(f"  - Rows: {df.shape[0]}")
print(f"  - Columns: {df.shape[1]}")

# Store original data for comparison
original_df = df.copy()

# Identify target variable
target = 'SalePrice'
print(f"\n✓ Target variable identified: {target}")

# Identify numerical and categorical columns
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

print(f"\n✓ Feature types identified:")
print(f"  - Numerical features: {len(numerical_cols)}")
print(f"  - Categorical features: {len(categorical_cols)}")

# Remove target and Id from numerical columns for processing
if 'Id' in numerical_cols:
    numerical_cols.remove('Id')
if target in numerical_cols:
    numerical_cols.remove(target)

# ============================================================================
# STEP 2: MISSING VALUE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: MISSING VALUE ANALYSIS")
print("=" * 80)

# Calculate missing values
missing_data = pd.DataFrame({
    'Missing Count': df.isnull().sum(),
    'Missing Percentage': (df.isnull().sum() / len(df)) * 100
})
missing_data = missing_data[missing_data['Missing Count'] > 0].sort_values(
    'Missing Percentage', ascending=False
)

print(f"\n✓ Columns with missing values: {len(missing_data)}")
print("\nMissing value summary (sorted by percentage):")
print(missing_data.to_string())

# Identify columns with >50% missing values
high_missing_cols = missing_data[missing_data['Missing Percentage'] > 50].index.tolist()
print(f"\n✓ Columns with >50% missing values: {high_missing_cols}")

# ============================================================================
# STEP 3: DATA CLEANING - DROP IRRELEVANT COLUMNS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: DATA CLEANING - DROP IRRELEVANT COLUMNS")
print("=" * 80)

# Columns to drop
columns_to_drop = ['Id'] + high_missing_cols
print(f"\n✓ Columns to drop:")
for col in columns_to_drop:
    reason = "Irrelevant identifier" if col == 'Id' else f">50% missing ({missing_data.loc[col, 'Missing Percentage']:.1f}%)"
    print(f"  - {col}: {reason}")

# Drop columns
df_cleaned = df.drop(columns=columns_to_drop)
print(f"\n✓ Dropped {len(columns_to_drop)} columns")
print(f"  - Remaining columns: {df_cleaned.shape[1]}")

# Update numerical and categorical column lists
numerical_cols_cleaned = [col for col in numerical_cols if col in df_cleaned.columns]
categorical_cols_cleaned = [col for col in categorical_cols if col in df_cleaned.columns]

# ============================================================================
# STEP 4: HANDLE MISSING VALUES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: HANDLE MISSING VALUES")
print("=" * 80)

# Store missing value handling decisions
missing_decisions = {}

# 4a. Numerical columns - fill with median (more robust to outliers than mean)
print("\n--- Numerical Columns ---")
for col in numerical_cols_cleaned:
    if df_cleaned[col].isnull().sum() > 0:
        median_val = df_cleaned[col].median()
        df_cleaned[col].fillna(median_val, inplace=True)
        missing_decisions[col] = f"Filled with median ({median_val:.2f})"
        print(f"  - {col}: {missing_decisions[col]}")

# 4b. Categorical columns - analyze each and decide
print("\n--- Categorical Columns ---")
for col in categorical_cols_cleaned:
    missing_count = df_cleaned[col].isnull().sum()
    if missing_count > 0:
        # Check if 'NA' has special meaning (like 'No Basement', 'No Garage', etc.)
        # Based on data_description.txt, these columns have 'NA' as valid category:
        na_meaning_cols = ['Alley', 'BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 
                          'BsmtFinType2', 'FireplaceQu', 'GarageType', 'GarageFinish', 
                          'GarageQual', 'GarageCond', 'PoolQC', 'Fence', 'MiscFeature']
        
        if col in na_meaning_cols or col in ['MasVnrType']:
            # NA has meaning - fill with 'None'
            df_cleaned[col].fillna('None', inplace=True)
            missing_decisions[col] = f"Filled with 'None' (NA has special meaning)"
        else:
            # Fill with mode (most frequent value)
            mode_val = df_cleaned[col].mode()[0]
            df_cleaned[col].fillna(mode_val, inplace=True)
            missing_decisions[col] = f"Filled with mode ('{mode_val}')"
        print(f"  - {col}: {missing_decisions[col]}")

# Verify no missing values remain
remaining_missing = df_cleaned.isnull().sum().sum()
print(f"\n✓ Missing values handled. Remaining missing values: {remaining_missing}")

# Save cleaned dataset
df_cleaned.to_csv('../data/cleaned_data.csv', index=False)
print(f"✓ Saved cleaned_data.csv ({df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns)")

# ============================================================================
# STEP 5: OUTLIER DETECTION AND DOCUMENTATION
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: OUTLIER DETECTION AND DOCUMENTATION")
print("=" * 80)

# Focus on key numerical features for outlier detection
outlier_features = ['SalePrice', 'GrLivArea', 'LotArea', 'TotalBsmtSF', '1stFlrSF']
outlier_info = {}

for col in outlier_features:
    if col in df_cleaned.columns:
        Q1 = df_cleaned[col].quantile(0.25)
        Q3 = df_cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df_cleaned[(df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)]
        outlier_info[col] = {
            'count': len(outliers),
            'percentage': len(outliers) / len(df_cleaned) * 100,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }
        print(f"\n  {col}:")
        print(f"    - Outliers detected: {outlier_info[col]['count']} ({outlier_info[col]['percentage']:.2f}%)")
        print(f"    - Valid range: [{lower_bound:.2f}, {upper_bound:.2f}]")

# Remove extreme outliers from GrLivArea (common in Ames dataset)
# Houses with very large living area but low price are often errors
print("\n--- Removing Extreme Outliers ---")
before_outlier_removal = len(df_cleaned)

# Remove houses with >4000 sq ft GrLivArea (documented in Ames dataset paper)
extreme_outliers = df_cleaned[df_cleaned['GrLivArea'] > 4000]
if len(extreme_outliers) > 0:
    print(f"  - Found {len(extreme_outliers)} houses with GrLivArea > 4000 sq ft")
    print(f"    These are likely data entry errors or unusual properties")
    df_cleaned = df_cleaned[df_cleaned['GrLivArea'] <= 4000]
    print(f"  - Removed {before_outlier_removal - len(df_cleaned)} extreme outliers")

print(f"\n✓ Dataset size after outlier removal: {df_cleaned.shape[0]} rows")

# ============================================================================
# STEP 6: FEATURE ENGINEERING
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: FEATURE ENGINEERING")
print("=" * 80)

# Create new features
print("\n--- Creating New Features ---")

# 6.1 Total Square Footage
# WHY: Combines all livable space - most important predictor of house value
df_cleaned['TotalSF'] = df_cleaned['TotalBsmtSF'] + df_cleaned['1stFlrSF'] + df_cleaned['2ndFlrSF']
print(f"  ✓ TotalSF = TotalBsmtSF + 1stFlrSF + 2ndFlrSF")
print(f"    Range: {df_cleaned['TotalSF'].min():.0f} - {df_cleaned['TotalSF'].max():.0f} sq ft")

# 6.2 House Age
# WHY: Age significantly affects property value - newer homes typically worth more
current_year = 2024  # Using 2024 as reference year
df_cleaned['HouseAge'] = current_year - df_cleaned['YearBuilt']
print(f"  ✓ HouseAge = {current_year} - YearBuilt")
print(f"    Range: {df_cleaned['HouseAge'].min():.0f} - {df_cleaned['HouseAge'].max():.0f} years")

# 6.3 Years Since Remodel
# WHY: Recent renovations increase value, captures renovation impact
df_cleaned['YearsSinceRemod'] = current_year - df_cleaned['YearRemodAdd']
print(f"  ✓ YearsSinceRemod = {current_year} - YearRemodAdd")
print(f"    Range: {df_cleaned['YearsSinceRemod'].min():.0f} - {df_cleaned['YearsSinceRemod'].max():.0f} years")

# 6.4 Total Bathrooms
# WHY: Bathroom count is important for buyers, combines all bathroom types
df_cleaned['TotalBathrooms'] = (df_cleaned['FullBath'] + 
                                 0.5 * df_cleaned['HalfBath'] + 
                                 df_cleaned['BsmtFullBath'] + 
                                 0.5 * df_cleaned['BsmtHalfBath'])
print(f"  ✓ TotalBathrooms = FullBath + 0.5*HalfBath + BsmtFullBath + 0.5*BsmtHalfBath")
print(f"    Range: {df_cleaned['TotalBathrooms'].min():.1f} - {df_cleaned['TotalBathrooms'].max():.1f}")

# 6.5 Overall Score
# WHY: Combines quality and condition into single metric, easier for models
df_cleaned['OverallScore'] = df_cleaned['OverallQual'] * df_cleaned['OverallCond']
print(f"  ✓ OverallScore = OverallQual × OverallCond")
print(f"    Range: {df_cleaned['OverallScore'].min():.0f} - {df_cleaned['OverallScore'].max():.0f}")

# 6.6 Total Porch Area
# WHY: Outdoor living space adds value, combining multiple porch types
df_cleaned['TotalPorchSF'] = (df_cleaned['OpenPorchSF'] + 
                               df_cleaned['EnclosedPorch'] + 
                               df_cleaned['3SsnPorch'] + 
                               df_cleaned['ScreenPorch'])
print(f"  ✓ TotalPorchSF = OpenPorchSF + EnclosedPorch + 3SsnPorch + ScreenPorch")
print(f"    Range: {df_cleaned['TotalPorchSF'].min():.0f} - {df_cleaned['TotalPorchSF'].max():.0f} sq ft")

# 6.7 Has Garage (Binary)
# WHY: Presence of garage is important for many buyers
df_cleaned['HasGarage'] = (df_cleaned['GarageArea'] > 0).astype(int)
print(f"  ✓ HasGarage = 1 if GarageArea > 0, else 0")
print(f"    Distribution: {df_cleaned['HasGarage'].value_counts().to_dict()}")

# 6.8 Has Basement (Binary)
# WHY: Basement adds significant value
df_cleaned['HasBasement'] = (df_cleaned['TotalBsmtSF'] > 0).astype(int)
print(f"  ✓ HasBasement = 1 if TotalBsmtSF > 0, else 0")
print(f"    Distribution: {df_cleaned['HasBasement'].value_counts().to_dict()}")

# 6.9 Has Fireplace (Binary)
# WHY: Fireplace is desirable feature
df_cleaned['HasFireplace'] = (df_cleaned['Fireplaces'] > 0).astype(int)
print(f"  ✓ HasFireplace = 1 if Fireplaces > 0, else 0")
print(f"    Distribution: {df_cleaned['HasFireplace'].value_counts().to_dict()}")

# 6.10 Is Remodeled (Binary)
# WHY: Remodeled homes may have different value patterns
df_cleaned['IsRemodeled'] = (df_cleaned['YearBuilt'] != df_cleaned['YearRemodAdd']).astype(int)
print(f"  ✓ IsRemodeled = 1 if YearBuilt ≠ YearRemodAdd, else 0")
print(f"    Distribution: {df_cleaned['IsRemodeled'].value_counts().to_dict()}")

print(f"\n✓ Created 10 new engineered features")

# ============================================================================
# STEP 7: CLASSIFICATION TARGET CREATION (price_class)
# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: CLASSIFICATION TARGET CREATION (price_class)")
print("=" * 80)

# Use quantile-based binning for balanced classes
print("\n--- Creating price_class based on SalePrice quantiles ---")

# Calculate quantiles
q33 = df_cleaned['SalePrice'].quantile(0.33)
q66 = df_cleaned['SalePrice'].quantile(0.66)

print(f"  - 33rd percentile: ${q33:,.0f}")
print(f"  - 66th percentile: ${q66:,.0f}")

# Create price_class
def assign_price_class(price):
    if price <= q33:
        return 'low'
    elif price <= q66:
        return 'medium'
    else:
        return 'high'

df_cleaned['price_class'] = df_cleaned['SalePrice'].apply(assign_price_class)

# Display distribution
class_distribution = df_cleaned['price_class'].value_counts()
print(f"\n✓ price_class distribution:")
for cls, count in class_distribution.items():
    pct = count / len(df_cleaned) * 100
    print(f"    - {cls}: {count} ({pct:.1f}%)")

# Store thresholds for documentation
price_class_thresholds = {'low_max': q33, 'medium_max': q66}

# ============================================================================
# STEP 8: ENCODING CATEGORICAL VARIABLES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 8: ENCODING CATEGORICAL VARIABLES")
print("=" * 80)

# Separate encoding strategies
# Ordinal features: Use Label Encoding (preserves order)
# Nominal features: Use One-Hot Encoding (no order implied)

# Identify ordinal features (those with quality/condition rankings)
ordinal_features = [
    'ExterQual', 'ExterCond', 'BsmtQual', 'BsmtCond', 'BsmtExposure',
    'BsmtFinType1', 'BsmtFinType2', 'HeatingQC', 'KitchenQual', 
    'FireplaceQu', 'GarageQual', 'GarageCond'
]

# Filter to existing columns
ordinal_features = [col for col in ordinal_features if col in df_cleaned.columns]
nominal_features = [col for col in categorical_cols_cleaned if col not in ordinal_features]

print(f"\n--- Encoding Strategy ---")
print(f"  - Ordinal features (Label Encoding): {len(ordinal_features)}")
print(f"  - Nominal features (One-Hot Encoding): {len(nominal_features)}")

# 8a. Label Encoding for ordinal features
print("\n--- Label Encoding (Ordinal Features) ---")
label_encoders = {}
for col in ordinal_features:
    le = LabelEncoder()
    df_cleaned[col + '_encoded'] = le.fit_transform(df_cleaned[col].astype(str))
    label_encoders[col] = le
    print(f"  ✓ {col} → {col}_encoded")

# 8b. One-Hot Encoding for nominal features
print("\n--- One-Hot Encoding (Nominal Features) ---")
print(f"  Original shape: {df_cleaned.shape}")

# Apply one-hot encoding
df_encoded = pd.get_dummies(df_cleaned, columns=nominal_features, drop_first=True)
print(f"  After encoding: {df_encoded.shape}")

# Drop original ordinal columns (keep encoded versions)
df_encoded = df_encoded.drop(columns=[col for col in ordinal_features if col in df_encoded.columns])
print(f"  After dropping original ordinal columns: {df_encoded.shape}")

# ============================================================================
# STEP 9: SCALING (ANALYSIS AND DECISION)
# ============================================================================
print("\n" + "=" * 80)
print("STEP 9: SCALING ANALYSIS")
print("=" * 80)

# Analyze need for scaling
print("\n--- Feature Value Ranges ---")
numerical_for_scaling = ['TotalSF', 'HouseAge', 'TotalBathrooms', 'OverallScore', 
                         'GrLivArea', 'LotArea', 'TotalBsmtSF', 'GarageArea']

for col in numerical_for_scaling:
    if col in df_encoded.columns:
        print(f"  {col}: [{df_encoded[col].min():.0f}, {df_encoded[col].max():.0f}]")

print("\n--- Scaling Decision ---")
print("  Scaling is NOT applied in this preprocessing step because:")
print("  1. Tree-based models (Random Forest, XGBoost) don't require scaling")
print("  2. Linear models benefit from scaling - can be applied during model training")
print("  3. Keeping unscaled values preserves interpretability")
print("  4. Scaling should be part of the model pipeline to prevent data leakage")
print("\n  ✓ Recommendation: Apply StandardScaler or MinMaxScaler during model training")

# ============================================================================
# STEP 10: FINAL OUTPUT
# ============================================================================
print("\n" + "=" * 80)
print("STEP 10: FINAL OUTPUT")
print("=" * 80)

# Separate features and targets
X = df_encoded.drop(columns=['SalePrice', 'price_class'])
y_regression = df_encoded['SalePrice']
y_classification = df_encoded['price_class']

# Encode price_class for output
price_class_mapping = {'low': 0, 'medium': 1, 'high': 2}
y_classification_encoded = y_classification.map(price_class_mapping)

print(f"\n✓ Final dataset prepared:")
print(f"  - Features (X): {X.shape}")
print(f"  - Regression target (SalePrice): {y_regression.shape}")
print(f"  - Classification target (price_class): {y_classification_encoded.shape}")

# Save processed dataset
processed_df = pd.concat([X, y_regression, y_classification_encoded.rename('price_class')], axis=1)
processed_df.to_csv('../data/processed_data.csv', index=False)
print(f"\n✓ Saved processed_data.csv ({processed_df.shape[0]} rows, {processed_df.shape[1]} columns)")

# Save feature names for reference
feature_names = X.columns.tolist()
with open('feature_names.txt', 'w') as f:
    f.write('\n'.join(feature_names))
print(f"✓ Saved feature_names.txt ({len(feature_names)} features)")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

print(f"\n--- Original Dataset ---")
print(f"  Rows: {original_df.shape[0]}")
print(f"  Columns: {original_df.shape[1]}")
print(f"  Missing values: {original_df.isnull().sum().sum()}")

print(f"\n--- Cleaned Dataset (cleaned_data.csv) ---")
print(f"  Rows: {df_cleaned.shape[0]}")
print(f"  Columns: {df_cleaned.shape[1]}")
print(f"  Missing values: {df_cleaned.isnull().sum().sum()}")

print(f"\n--- Processed Dataset (processed_data.csv) ---")
print(f"  Rows: {processed_df.shape[0]}")
print(f"  Columns: {processed_df.shape[1]}")
print(f"  Numerical features: {len(X.select_dtypes(include=['int64', 'float64', 'uint8']).columns)}")

print("\n" + "=" * 80)
print("PREPROCESSING COMPLETE!")
print("=" * 80)
