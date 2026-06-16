"""
XGBoost Regression Model Training for Housing Price Prediction
Author: pooya jafarpour
Dataset: Ames Housing Dataset (preprocessed)
Purpose: Compare XGBoost against Linear Regression and Random Forest
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor

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

# Columns to exclude from features (EXACT same as previous models)
exclude_columns = ['SalePrice', 'price_class']

# Define features (X) and target (y)
X = df.drop(columns=[col for col in exclude_columns if col in df.columns])
y = df['SalePrice']

print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Check for missing values (EXACT same handling as previous models)
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

# EXACT same split as Linear Regression and Random Forest (test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42
)

print(f"Training set size: {X_train.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")

# =============================================================================
# 4. TRAIN XGBOOST MODEL
# =============================================================================
print("\n" + "=" * 70)
print("TRAINING XGBOOST MODEL")
print("=" * 70)

# Initialize XGBoost with baseline parameters
# n_estimators=100    → Build 100 boosting rounds (gradient boosted trees)
# max_depth=6         → Maximum tree depth (controls model complexity)
# learning_rate=0.1   → Step size shrinkage (lower = more conservative learning)
# random_state=42     → Ensures reproducible results across runs
model = XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)

print("Fitting XGBoost model...")
print(f"  • Boosting rounds: {model.n_estimators}")
print(f"  • Max depth: {model.max_depth}")
print(f"  • Learning rate: {model.learning_rate}")
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
print("XGBOOST RESULTS")
print("=" * 70)
print(f"\nTraining Set Performance:")
print(f"  RMSE: ${train_rmse:,.2f}")
print(f"  R²: {train_r2:.4f}")

print(f"\nTest Set Performance:")
print(f"  RMSE: ${test_rmse:,.2f}")
print(f"  R²: {test_r2:.4f}")

# =============================================================================
# 6. FEATURE IMPORTANCE ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("TOP 20 MOST IMPORTANT FEATURES")
print("=" * 70)

# Get feature importance scores
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

# Display top 20 features
print("\nRank  Feature                              Importance Score")
print("-" * 70)
for idx, row in feature_importance.head(20).iterrows():
    rank = feature_importance.index.get_loc(idx) + 1
    print(f"{rank:3d}.  {row['Feature']:36s}  {row['Importance']:.4f}")

# =============================================================================
# 7. MODEL COMPARISON
# =============================================================================
print("\n" + "=" * 70)
print("MODEL COMPARISON TABLE")
print("=" * 70)

# Create comparison table
comparison_data = {
    'Metric': ['Test RMSE', 'Test R²'],
    'Linear Regression': ['$22,974.15', '0.8994'],
    'Random Forest': ['$23,133.58', '0.8980'],
    'XGBoost': [f'${test_rmse:,.2f}', f'{test_r2:.4f}']
}

comparison_df = pd.DataFrame(comparison_data)
print("\n" + comparison_df.to_string(index=False))

# =============================================================================
# 8. TECHNICAL INTERPRETATION
# =============================================================================
print("\n" + "=" * 70)
print("TECHNICAL INTERPRETATION")
print("=" * 70)

# Calculate average house price for context
avg_price = y.mean()
rmse_percentage = (test_rmse / avg_price) * 100

# Overfitting analysis
train_test_rmse_gap = train_rmse - test_rmse
train_test_r2_gap = train_r2 - test_r2

print(f"\n📊 Performance Analysis:")
print(f"   Average house price: ${avg_price:,.2f}")
print(f"   RMSE as % of avg price: {rmse_percentage:.1f}%")

print(f"\n🔍 Bias-Variance Trade-off:")
print(f"\n   Linear Regression (High Bias, Low Variance):")
print(f"   • Simple linear model with strong assumptions")
print(f"   • Can't capture complex non-linear patterns → UNDERFITTING")
print(f"   • Generalizes well but has limited learning capacity")

print(f"\n   Random Forest (Lower Bias, Higher Variance):")
print(f"   • Ensemble of 100 decision trees averaging predictions")
print(f"   • Captures non-linear relationships and feature interactions")
print(f"   • Risk of overfitting if trees are too deep (mitigated by averaging)")

print(f"\n   XGBoost (Balanced Bias-Variance):")
print(f"   • Sequential boosting: each tree corrects previous errors")
print(f"   • Regularization (learning_rate, max_depth) prevents overfitting")
print(f"   • Often achieves best generalization through careful error correction")

print(f"\n📈 Overfitting Behavior:")
print(f"   Train RMSE: ${train_rmse:,.2f}")
print(f"   Test RMSE:  ${test_rmse:,.2f}")
print(f"   Gap:        ${abs(train_test_rmse_gap):,.2f}")

if train_r2 > test_r2 + 0.05:
    print(f"\n   ⚠ Signs of OVERFITTING detected:")
    print(f"   • Training R² ({train_r2:.4f}) significantly exceeds Test R² ({test_r2:.4f})")
    print(f"   • Model memorizes training patterns that don't generalize")
    print(f"   • Consider: reducing max_depth, increasing learning_rate regularization")
elif train_r2 < test_r2:
    print(f"\n   ✓ EXCELLENT generalization:")
    print(f"   • Test performance meets or exceeds training performance")
    print(f"   • No signs of overfitting")
else:
    print(f"\n   ✓ GOOD generalization:")
    print(f"   • Training and test performance are well-aligned")
    print(f"   • Minimal overfitting detected")

print(f"\n💡 Why XGBoost Performance:")

# Compare with existing models
linear_rmse = 22974.15
rf_rmse = 23133.58

if test_rmse < linear_rmse and test_rmse < rf_rmse:
    print(f"\n   🏆 XGBoost OUTPERFORMS both models:")
    print(f"   • Better than Linear Regression by ${linear_rmse - test_rmse:,.2f}")
    print(f"   • Better than Random Forest by ${rf_rmse - test_rmse:,.2f}")
    print(f"\n   Reasons:")
    print(f"   • Sequential error correction learns residual patterns missed by trees")
    print(f"   • Built-in regularization prevents overfitting")
    print(f"   • Handles feature interactions more efficiently than Random Forest")
    print(f"\n   ✅ RECOMMENDATION: Deploy XGBoost for best predictive accuracy")
    
elif test_rmse < linear_rmse:
    print(f"\n   📊 XGBoost OUTPERFORMS Linear Regression:")
    print(f"   • Better by ${linear_rmse - test_rmse:,.2f}")
    print(f"   • But slightly worse than Random Forest by ${test_rmse - rf_rmse:,.2f}")
    print(f"\n   Possible reasons:")
    print(f"   • Baseline parameters may not be optimal for this dataset")
    print(f"   • Random Forest's averaging may better handle this data's variance")
    print(f"\n   💡 RECOMMENDATION: Consider hyperparameter tuning for XGBoost")
    
else:
    print(f"\n   📊 XGBoost performs COMPARABLE to existing models:")
    print(f"   • Difference from Linear Regression: ${abs(test_rmse - linear_rmse):,.2f}")
    print(f"   • Difference from Random Forest: ${abs(test_rmse - rf_rmse):,.2f}")
    print(f"\n   Possible reasons:")
    print(f"   • Housing price relationships may be relatively simple")
    print(f"   • Baseline parameters need optimization")
    print(f"   • Dataset size or feature quality limits complex model benefits")
    print(f"\n   💡 RECOMMENDATION: Linear Regression offers simplicity with similar accuracy")

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
