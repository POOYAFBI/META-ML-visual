# Dataset Comparison Summary

## Quick Reference

### Dataset A: Full Feature Engineering
- **File:** `processed_data.csv`
- **Shape:** 1456 rows × 211 columns
- **Features:** 209 (excluding targets)
- **Targets:** SalePrice, price_class
- **Includes:** Raw features + Encoded features + 10 Engineered features

### Dataset B: Minimal Feature Engineering
- **File:** `processed_data_minimal_fe.csv`
- **Shape:** 1456 rows × 201 columns
- **Features:** 199 (excluding targets)
- **Targets:** SalePrice, price_class
- **Includes:** Raw features + Encoded features (NO engineered features)

## Removed Engineered Features (10 total)

| Feature | Type | Removed Because |
|---------|------|-----------------|
| TotalSF | Aggregation | Sum of TotalBsmtSF + 1stFlrSF + 2ndFlrSF |
| HouseAge | Derived Metric | Calculated from YearBuilt |
| YearsSinceRemod | Derived Metric | Calculated from YearRemodAdd |
| TotalBathrooms | Aggregation | Weighted sum of all bathroom features |
| OverallScore | Composite Indicator | Product of OverallQual × OverallCond |
| TotalPorchSF | Aggregation | Sum of all porch areas |
| HasGarage | Binary Indicator | Threshold on GarageArea |
| HasBasement | Binary Indicator | Threshold on TotalBsmtSF |
| HasFireplace | Binary Indicator | Threshold on Fireplaces |
| IsRemodeled | Binary Indicator | Comparison of YearBuilt vs YearRemodAdd |

## Current Model Performance (Full FE Dataset)

Based on previous training results:

### Regression Task (RMSE - lower is better)

1. **Linear Regression:** BEST performer
2. **XGBoost:** Second place
3. **Random Forest:** Third place

### Why This Matters

The current ranking suggests that Linear Regression benefits significantly from the 10 engineered features. These features provide:

- **Explicit aggregations** that Linear models cannot compute automatically
- **Interaction terms** (like OverallScore = Quality × Condition)
- **Non-linear transformations** (like age calculations)
- **Binary indicators** that help with threshold-based relationships

Tree-based models (Random Forest, XGBoost) can naturally discover these patterns through splits, so they may not need pre-computed features.

## Experimental Hypothesis

**Hypothesis:** Feature Engineering disproportionately benefits Linear Regression compared to tree-based models.

**Expected Results on Minimal FE Dataset:**
- Linear Regression: Significant performance DROP
- XGBoost: Minimal or no performance drop
- Random Forest: Minimal or no performance drop

**If hypothesis confirmed:**
- Tree-based models will outperform Linear Regression on minimal FE dataset
- Model ranking will change from Linear > XGBoost > RF to XGBoost > RF > Linear

## Next Steps for Experimentation

### Phase 1: Train on Minimal FE Dataset ✓ READY
Train each model on `processed_data_minimal_fe.csv`:
- Linear Regression
- Random Forest  
- XGBoost

Use the same hyperparameters as previous training runs for fair comparison.

### Phase 2: Calculate Performance Metrics
Record for each model on minimal FE dataset:
- RMSE (regression)
- R² Score (regression)
- MAE (regression)
- Accuracy (classification)
- F1 Score (classification)

### Phase 3: Compute FE Impact Scores
Calculate for each model:

```
FE_Impact_Score = ((RMSE_Full_FE - RMSE_Minimal_FE) / RMSE_Full_FE) × 100%
```

Positive score = model performs worse without FE (depends on FE)
Higher score = greater dependence on feature engineering

### Phase 4: Comparative Analysis
Compare impact scores to determine:
1. Which model is most dependent on feature engineering?
2. Which model is most robust without feature engineering?
3. Does model ranking change?

## Training Commands

To train models on the minimal FE dataset, modify your existing training scripts:

### Linear Regression
```bash
# Update train_linear.py to use processed_data_minimal_fe.csv
python train_linear.py
```

### Random Forest
```bash
# Update train_rf.py to use processed_data_minimal_fe.csv
python train_rf.py
```

### XGBoost
```bash
# Update train_xgb.py to use processed_data_minimal_fe.csv
python train_xgb.py
```

## Expected File Outputs

After training, you should have:

1. **Model files:**
   - `linear_model_minimal_fe.pkl`
   - `rf_model_minimal_fe.pkl`
   - `xgb_model_minimal_fe.pkl`

2. **Summary reports:**
   - `LINEAR_TRAINING_SUMMARY_MINIMAL_FE.md`
   - `RF_TRAINING_SUMMARY_MINIMAL_FE.md`
   - `XGB_TRAINING_SUMMARY_MINIMAL_FE.md`

3. **Comparative analysis:**
   - `FE_IMPACT_ANALYSIS.md` (to be created after all models trained)

---

**Status:** Dataset creation and audit COMPLETE ✓  
**Next Action:** Train models on `processed_data_minimal_fe.csv`  
**Date Created:** 2026-06-13
