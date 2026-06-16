"""
Random Forest Regression Model Training for Housing Price Prediction
Dataset: MINIMAL Feature Engineering (processed_data_minimal_fe.csv)
Purpose: Measure impact of removing 10 engineered features
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
print("LOADING MINIMAL FE DATASET")
print("=" * 70)

df = pd.read_csv('../data/processed_data_minimal_fe.csv')
print(f"Dataset shape: {df.shape}")
print(f"Total features: {df.shape[1] - 2}")  # Excluding SalePrice and price_class
print(f"Dataset: MINIMAL Feature Engineering (10 engineered features removed)")

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

# EXACT same split logic as Full FE training (test_size=0.2, random_state=42)
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

# Initialize Random Forest with EXACT same parameters as Full FE
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
print("RANDOM FOREST RESULTS - MINIMAL FE")
print("=" * 70)
print(f"\nTraining Set Performance:")
print(f"  RMSE: ${train_rmse:,.2f}")
print(f"  R²: {train_r2:.4f}")

print(f"\nTest Set Performance:")
print(f"  RMSE: ${test_rmse:,.2f}")
print(f"  R²: {test_r2:.4f}")

# =============================================================================
# 6. COMPARISON WITH FULL FE
# =============================================================================
print("\n" + "=" * 70)
print("COMPARISON: FULL FE vs MINIMAL FE")
print("=" * 70)

# Full FE results (from RF_TRAINING_SUMMARY.md)
full_fe_test_rmse = 23133.58
full_fe_test_r2 = 0.8980

print(f"\n📊 Test Set Comparison:")
print(f"\n  Full FE Dataset:")
print(f"    RMSE: ${full_fe_test_rmse:,.2f}")
print(f"    R²: {full_fe_test_r2:.4f}")

print(f"\n  Minimal FE Dataset:")
print(f"    RMSE: ${test_rmse:,.2f}")
print(f"    R²: {test_r2:.4f}")

# Calculate impact
rmse_change = test_rmse - full_fe_test_rmse
rmse_impact_pct = (rmse_change / full_fe_test_rmse) * 100

r2_change = test_r2 - full_fe_test_r2
r2_impact_pct = ((full_fe_test_r2 - test_r2) / full_fe_test_r2) * 100

print(f"\n  Impact of Removing Engineered Features:")
print(f"    RMSE Change: ${rmse_change:+,.2f} ({rmse_impact_pct:+.2f}%)")
print(f"    R² Change: {r2_change:+.4f} ({r2_impact_pct:+.2f}%)")

# Interpretation
print(f"\n💡 Interpretation:")
if rmse_impact_pct > 5:
    print(f"   ⚠ SIGNIFICANT DEGRADATION:")
    print(f"   • Random Forest depends on engineered features")
    print(f"   • RMSE increased by {rmse_impact_pct:.2f}%")
    print(f"   • Pre-computed features helped the model")
elif rmse_impact_pct > 1:
    print(f"   ~ MODERATE DEGRADATION:")
    print(f"   • Some dependence on engineered features")
    print(f"   • RMSE increased by {rmse_impact_pct:.2f}%")
elif rmse_impact_pct > -1:
    print(f"   ✓ MINIMAL IMPACT:")
    print(f"   • Random Forest is robust without engineered features")
    print(f"   • Can discover patterns from raw features automatically")
    print(f"   • RMSE change is negligible ({rmse_impact_pct:.2f}%)")
else:
    print(f"   ✓ IMPROVED PERFORMANCE:")
    print(f"   • Model performs better without engineered features")
    print(f"   • RMSE decreased by {abs(rmse_impact_pct):.2f}%")
    print(f"   • Engineered features may have introduced noise or redundancy")

# =============================================================================
# 7. SAVE RESULTS
# =============================================================================

# Create summary report
report_lines = []
report_lines.append("# Random Forest Training Summary - Minimal FE")
report_lines.append("")
report_lines.append("## Dataset")
report_lines.append("- **File:** `processed_data_minimal_fe.csv`")
report_lines.append(f"- **Features:** {X.shape[1]} (199 features)")
report_lines.append(f"- **Samples:** {len(df)}")
report_lines.append("- **Feature Engineering:** MINIMAL (10 engineered features removed)")
report_lines.append("")
report_lines.append("### Removed Engineered Features")
report_lines.append("1. TotalSF")
report_lines.append("2. HouseAge")
report_lines.append("3. YearsSinceRemod")
report_lines.append("4. TotalBathrooms")
report_lines.append("5. OverallScore")
report_lines.append("6. TotalPorchSF")
report_lines.append("7. HasGarage")
report_lines.append("8. HasBasement")
report_lines.append("9. HasFireplace")
report_lines.append("10. IsRemodeled")
report_lines.append("")
report_lines.append("## Model Configuration")
report_lines.append("- **Algorithm:** Random Forest Regressor")
report_lines.append("- **n_estimators:** 100")
report_lines.append("- **random_state:** 42")
report_lines.append("- **n_jobs:** -1 (all CPU cores)")
report_lines.append("")
report_lines.append("## Model Performance")
report_lines.append("")
report_lines.append("### Training Set")
report_lines.append(f"- **RMSE:** ${train_rmse:,.2f}")
report_lines.append(f"- **R²:** {train_r2:.4f}")
report_lines.append("")
report_lines.append("### Test Set")
report_lines.append(f"- **RMSE:** ${test_rmse:,.2f}")
report_lines.append(f"- **R²:** {test_r2:.4f}")
report_lines.append("")
report_lines.append("## Overfitting Analysis")
report_lines.append("")
train_test_gap = train_rmse - test_rmse
train_r2_test_r2_gap = train_r2 - test_r2
if train_r2 > test_r2 + 0.05:
    report_lines.append("**Status:** Some overfitting detected")
    report_lines.append(f"- Training R² ({train_r2:.4f}) exceeds Test R² ({test_r2:.4f})")
    report_lines.append(f"- Gap: {train_r2_test_r2_gap:.4f}")
elif train_r2 < test_r2:
    report_lines.append("**Status:** Excellent generalization")
    report_lines.append("- Test performance meets or exceeds training performance")
else:
    report_lines.append("**Status:** Good generalization")
    report_lines.append("- Training and test performance are well-aligned")
report_lines.append("")
report_lines.append("## Comparison: Full FE vs Minimal FE")
report_lines.append("")
report_lines.append("| Metric | Full FE | Minimal FE | Change | Impact % |")
report_lines.append("|--------|---------|------------|--------|----------|")
report_lines.append(f"| Test RMSE | ${full_fe_test_rmse:,.2f} | ${test_rmse:,.2f} | ${rmse_change:+,.2f} | {rmse_impact_pct:+.2f}% |")
report_lines.append(f"| Test R² | {full_fe_test_r2:.4f} | {test_r2:.4f} | {r2_change:+.4f} | {r2_impact_pct:+.2f}% |")
report_lines.append("")
report_lines.append("## Interpretation")
report_lines.append("")
if rmse_impact_pct > 5:
    report_lines.append("**Finding:** Random Forest shows SIGNIFICANT DEPENDENCE on engineered features.")
    report_lines.append("")
    report_lines.append("**Evidence:**")
    report_lines.append(f"- Test RMSE increased by {rmse_impact_pct:.2f}%")
    report_lines.append(f"- Test R² decreased by {abs(r2_impact_pct):.2f}%")
    report_lines.append("")
    report_lines.append("**Explanation:**")
    report_lines.append("- Pre-computed features provided valuable signal")
    report_lines.append("- Model benefited from explicit feature engineering")
elif rmse_impact_pct > 1:
    report_lines.append("**Finding:** Random Forest shows MODERATE DEPENDENCE on engineered features.")
    report_lines.append("")
    report_lines.append("**Evidence:**")
    report_lines.append(f"- Test RMSE increased by {rmse_impact_pct:.2f}%")
    report_lines.append(f"- Test R² decreased by {abs(r2_impact_pct):.2f}%")
elif rmse_impact_pct < -1:
    report_lines.append("**Finding:** Random Forest IMPROVED without engineered features.")
    report_lines.append("")
    report_lines.append("**Evidence:**")
    report_lines.append(f"- Test RMSE decreased by {abs(rmse_impact_pct):.2f}%")
    report_lines.append(f"- Test R² improved")
    report_lines.append("")
    report_lines.append("**Explanation:**")
    report_lines.append("- Engineered features may have introduced redundancy or noise")
    report_lines.append("- Tree-based models can automatically discover patterns from raw features")
    report_lines.append("- Simplifying features improved generalization")
else:
    report_lines.append("**Finding:** Random Forest is ROBUST without engineered features.")
    report_lines.append("")
    report_lines.append("**Evidence:**")
    report_lines.append(f"- Test RMSE changed by only {rmse_impact_pct:.2f}%")
    report_lines.append("- Performance remained stable")
    report_lines.append("")
    report_lines.append("**Explanation:**")
    report_lines.append("- Tree-based models can automatically discover feature interactions")
    report_lines.append("- Decision trees naturally aggregate and threshold features")
    report_lines.append("- Minimal dependence on manual feature engineering")

report_lines.append("")
report_lines.append("---")
report_lines.append(f"*Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*")

# Save report
with open('RF_MINIMAL_FE_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print("\n✓ Saved: RF_MINIMAL_FE_SUMMARY.md")

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
