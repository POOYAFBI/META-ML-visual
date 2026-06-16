# Random Forest Training Summary - Minimal FE

## Dataset
- **File:** `processed_data_minimal_fe.csv`
- **Features:** 199 (199 features)
- **Samples:** 1456
- **Feature Engineering:** MINIMAL (10 engineered features removed)

### Removed Engineered Features
1. TotalSF
2. HouseAge
3. YearsSinceRemod
4. TotalBathrooms
5. OverallScore
6. TotalPorchSF
7. HasGarage
8. HasBasement
9. HasFireplace
10. IsRemodeled

## Model Configuration
- **Algorithm:** Random Forest Regressor
- **n_estimators:** 100
- **random_state:** 42
- **n_jobs:** -1 (all CPU cores)

## Model Performance

### Training Set
- **RMSE:** $9,871.03
- **R²:** 0.9838

### Test Set
- **RMSE:** $24,218.50
- **R²:** 0.8882

## Overfitting Analysis

**Status:** Some overfitting detected
- Training R² (0.9838) exceeds Test R² (0.8882)
- Gap: 0.0956

## Comparison: Full FE vs Minimal FE

| Metric | Full FE | Minimal FE | Change | Impact % |
|--------|---------|------------|--------|----------|
| Test RMSE | $23,133.58 | $24,218.50 | $+1,084.92 | +4.69% |
| Test R² | 0.8980 | 0.8882 | -0.0098 | +1.09% |

## Interpretation

**Finding:** Random Forest shows MODERATE DEPENDENCE on engineered features.

**Evidence:**
- Test RMSE increased by 4.69%
- Test R² decreased by 1.09%

---
*Generated: 2026-06-13 11:15:29*