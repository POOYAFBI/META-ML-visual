# Linear Regression Training Summary - Minimal FE

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

## Model Performance

### Training Set
- **RMSE:** $20,426.14
- **R²:** 0.9308

### Test Set
- **RMSE:** $23,239.24
- **R²:** 0.8971

## Comparison: Full FE vs Minimal FE

| Metric | Full FE | Minimal FE | Change | Impact % |
|--------|---------|------------|--------|----------|
| Test RMSE | $22,974.15 | $23,239.24 | $+265.09 | +1.15% |
| Test R² | 0.8994 | 0.8971 | -0.0023 | +0.26% |

## Interpretation

**Finding:** Linear Regression shows MODERATE DEPENDENCE on engineered features.

**Evidence:**
- Test RMSE increased by 1.15%
- Test R² decreased by 0.26%

---
*Generated: 2026-06-13 11:15:06*