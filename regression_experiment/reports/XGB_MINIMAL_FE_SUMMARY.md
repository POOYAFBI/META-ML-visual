# XGBoost Training Summary - Minimal FE

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
- **Algorithm:** XGBoost Regressor
- **n_estimators:** 100
- **max_depth:** 6
- **learning_rate:** 0.1
- **random_state:** 42

## Model Performance

### Training Set
- **RMSE:** $4,983.12
- **R²:** 0.9959

### Test Set
- **RMSE:** $24,618.88
- **R²:** 0.8845

## Overfitting Analysis

**Status:** Some overfitting detected
- Training R² (0.9959) exceeds Test R² (0.8845)
- Gap: 0.1114

## Comparison: Full FE vs Minimal FE

| Metric | Full FE | Minimal FE | Change | Impact % |
|--------|---------|------------|--------|----------|
| Test RMSE | $23,072.84 | $24,618.88 | $+1,546.04 | +6.70% |
| Test R² | 0.8986 | 0.8845 | -0.0141 | +1.57% |

## Top 20 Most Important Features

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | OverallQual | 0.4581 |
| 2 | GrLivArea | 0.0559 |
| 3 | GarageType_Detchd | 0.0399 |
| 4 | TotRmsAbvGrd | 0.0325 |
| 5 | CentralAir_Y | 0.0321 |
| 6 | LotShape_Reg | 0.0220 |
| 7 | GarageCars | 0.0213 |
| 8 | MSZoning_RM | 0.0206 |
| 9 | BsmtQual_encoded | 0.0179 |
| 10 | KitchenAbvGr | 0.0165 |
| 11 | BsmtFinSF1 | 0.0165 |
| 12 | GarageType_Attchd | 0.0155 |
| 13 | TotalBsmtSF | 0.0140 |
| 14 | Fireplaces | 0.0115 |
| 15 | Functional_Min1 | 0.0103 |
| 16 | GarageArea | 0.0103 |
| 17 | 1stFlrSF | 0.0097 |
| 18 | RoofStyle_Hip | 0.0094 |
| 19 | YearBuilt | 0.0075 |
| 20 | BsmtFinType1_encoded | 0.0065 |

## Interpretation

**Finding:** XGBoost shows SIGNIFICANT DEPENDENCE on engineered features.

**Evidence:**
- Test RMSE increased by 6.70%
- Test R² decreased by 1.57%

**Explanation:**
- Pre-computed features provided valuable signal
- Model benefited from explicit feature engineering

---
*Generated: 2026-06-13 11:15:49*