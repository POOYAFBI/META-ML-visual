"""
Random Forest Regression Model Training for Housing Price Prediction
Author: pooya jafarpour
Dataset: Ames Housing Dataset (preprocessed)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# =============================================================================
# 1. LOAD DATA
# =============================================================================
print("=" * 70)
print("LOADING PROCESSED DATA")
print("=" * 70)

df = pd.read_csv('../data/processed_data.csv')
print(f"Dataset shape: {df.shape}")
print(f"Total features: {df.shape[1] - 2}")  # Excluding SalePrice and price_class

# =============================================================================
# 2. DEFINE FEATURES AND TARGET
# =============================================================================
print("\n" + "=" * 70)
print("PREPARING FEATURES AND TARGET")
print("=" * 70)

# Columns to exclude from features
exclude_columns = ['SalePrice', 'price_class']

# Define features (X) and target (y)
X = df.drop(columns=[col for col in exclude_columns if col in df.columns])
y = df['SalePrice']

print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Check for missing values
missing_count = X.isnull().sum().sum()
if missing_count > 0:
    print(f"\n⚠ Found {missing_count} missing values - filling with column means")
    X = X.fillna(X.mean())
    print("✓ Missing values handled")

print(f"\nTarget statistics:")
print(f"  Mean: ${y.mean():,.2f}")
print(f"  Median: ${y.median():,.2f}")
print(f"  Min: ${y.min():,.2f}")
print(f"  Max: ${y.max():,.2f}")

# =============================================================================
# 3. TRAIN/TEST SPLIT
# =============================================================================
print("\n" + "=" * 70)
print("SPLITTING DATA")
print("=" * 70)

# EXACT same split logic as Linear Regression (test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42
)

print(f"Training set size: {X_train.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")

# =============================================================================
# 4. TRAIN RANDOM FOREST MODEL
# =============================================================================
print("\n" + "=" * 70)
print("TRAINING RANDOM FOREST MODEL")
print("=" * 70)

# Initialize Random Forest with specified parameters
# n_estimators=100  → Build 100 decision trees (more trees = better predictions)
# random_state=42   → Ensures reproducible results across runs
# n_jobs=-1         → Use all CPU cores for faster training
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("Fitting Random Forest model...")
print(f"  • Building {model.n_estimators} decision trees")
print(f"  • Using all CPU cores for parallel training")
model.fit(X_train, y_train)
print("✓ Training completed!")

# =============================================================================
# 5. MODEL EVALUATION
# =============================================================================
print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

# Make predictions
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Calculate metrics for training set
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
train_r2 = r2_score(y_train, y_pred_train)

# Calculate metrics for test set
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_r2 = r2_score(y_test, y_pred_test)

# Print results
print("\n" + "=" * 70)
print("RANDOM FOREST RESULTS")
print("=" * 70)
print(f"\nTraining Set Performance:")
print(f"  RMSE: ${train_rmse:,.2f}")
print(f"  R²: {train_r2:.4f}")

print(f"\nTest Set Performance:")
print(f"  RMSE: ${test_rmse:,.2f}")
print(f"  R²: {test_r2:.4f}")

# =============================================================================
# 6. BASIC INTERPRETATION
# =============================================================================
print("\n" + "=" * 70)
print("MODEL INTERPRETATION & COMPARISON")
print("=" * 70)

# Calculate average house price for context
avg_price = y.mean()
rmse_percentage = (test_rmse / avg_price) * 100

print(f"\n📊 Performance Analysis:")
print(f"   Average house price: ${avg_price:,.2f}")
print(f"   RMSE as % of avg price: {rmse_percentage:.1f}%")

# Interpretation
print(f"\n💡 Key Insights:")
print(f"\n1️⃣  Performance Comparison:")
print(f"    Random Forest typically IMPROVES over Linear Regression because:")
print(f"    • It captures NON-LINEAR relationships (e.g., doubling square footage")
print(f"      doesn't necessarily double the price)")
print(f"    • It automatically detects FEATURE INTERACTIONS (e.g., premium")
print(f"      neighborhood + large lot size creates synergy effects)")
print(f"    • It's ROBUST to outliers (extreme values don't skew the entire model)")

print(f"\n2️⃣  Why Random Forest Works Better:")
print(f"    • Builds {model.n_estimators} different decision trees, each learning different")
print(f"      patterns from the data")
print(f"    • Averages predictions from all trees → reduces overfitting and variance")
print(f"    • Can model complex, non-linear patterns that Linear Regression misses")

# Performance quality assessment
if test_r2 >= 0.85:
    print(f"\n3️⃣  Overall Assessment: EXCELLENT ✓")
    print(f"    The model explains {test_r2*100:.1f}% of price variance - strong predictive power!")
elif test_r2 >= 0.75:
    print(f"\n3️⃣  Overall Assessment: GOOD ✓")
    print(f"    The model explains {test_r2*100:.1f}% of price variance - solid performance.")
elif test_r2 >= 0.60:
    print(f"\n3️⃣  Overall Assessment: MODERATE ~")
    print(f"    The model explains {test_r2*100:.1f}% of price variance - room for improvement.")
else:
    print(f"\n3️⃣  Overall Assessment: NEEDS IMPROVEMENT ✗")
    print(f"    The model only explains {test_r2*100:.1f}% of price variance.")

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
