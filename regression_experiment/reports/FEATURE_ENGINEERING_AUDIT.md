# Feature Engineering Audit Report

## Executive Summary

**Date:** 2026-06-13 11:04:24
**Purpose:** Create controlled experiment to measure Feature Engineering impact on ML models

### Dataset Comparison

| Metric | Full FE Dataset | Minimal FE Dataset | Difference |
|--------|-----------------|-----------------------|------------|
| Total Features | 209 | 199 | -10 (-4.8%) |
| Raw Features | 36 | 36 | 0 |
| Encoded Features | 163 | 163 | 0 |
| Engineered Features | 10 | 0 | -10 |
| Samples | 1456 | 1456 | 0 |

## Scientific Rationale

### Experimental Design

This audit creates two datasets for a controlled experiment:

**Dataset A (Full FE):** `processed_data.csv`
- Contains all raw features, encoded features, AND engineered features
- Total: 209 features
- Includes aggregations, ratios, composite indicators, derived metrics

**Dataset B (Minimal FE):** `processed_data_minimal_fe.csv`
- Contains only raw features and encoded categorical variables
- Total: 199 features
- NO aggregations, ratios, composite indicators, or derived metrics

### Research Hypothesis

**Current Observation:**
- Linear Regression performs BEST on full FE dataset
- XGBoost performs SECOND
- Random Forest performs THIRD

**Hypothesis:**
Extensive feature engineering may disproportionately benefit Linear Regression because:
1. Linear models cannot create non-linear interactions automatically
2. Engineered features provide explicit non-linear relationships
3. Tree-based models (RF, XGBoost) can discover these patterns naturally

**Expected Results on Minimal FE Dataset:**
- Tree-based models (XGBoost, RF) should maintain or improve performance
- Linear Regression performance should decrease significantly
- This would confirm FE benefits Linear models disproportionately

### Comparison Metrics

For each model (Linear Regression, Random Forest, XGBoost), measure:

1. **Regression Performance:**
   - Root Mean Squared Error (RMSE)
   - R² Score
   - Mean Absolute Error (MAE)

2. **Classification Performance:**
   - Accuracy
   - Precision, Recall, F1-Score (per class)

3. **Performance Delta:**
   - Calculate: `(Full_FE_Score - Minimal_FE_Score) / Full_FE_Score × 100%`
   - Shows percentage performance drop when FE removed
   - Higher delta = model benefited more from FE

## Detailed Feature Categorization

### Category A: Raw Numerical Features (KEPT: 36)

These are original features from the dataset with no transformations except missing value imputation.

| Feature | Description |
|---------|-------------|
| MSSubClass | Type of dwelling |
| LotFrontage | Linear feet of street connected to property |
| LotArea | Lot size in square feet |
| OverallQual | Overall material and finish quality (1-10) |
| OverallCond | Overall condition rating (1-10) |
| YearBuilt | Original construction year |
| YearRemodAdd | Remodel year |
| MasVnrArea | Masonry veneer area |
| BsmtFinSF1 | Type 1 finished basement area |
| BsmtFinSF2 | Type 2 finished basement area |
| BsmtUnfSF | Unfinished basement area |
| TotalBsmtSF | Total basement area |
| 1stFlrSF | First floor area |
| 2ndFlrSF | Second floor area |
| LowQualFinSF | Low quality finished area |
| GrLivArea | Above grade living area |
| BsmtFullBath | Basement full bathrooms |
| BsmtHalfBath | Basement half bathrooms |
| FullBath | Full bathrooms above grade |
| HalfBath | Half bathrooms above grade |
| BedroomAbvGr | Bedrooms above grade |
| KitchenAbvGr | Kitchens above grade |
| TotRmsAbvGrd | Total rooms above grade |
| Fireplaces | Number of fireplaces |
| GarageYrBlt | Year garage built |
| GarageCars | Garage capacity in cars |
| GarageArea | Garage area in square feet |
| WoodDeckSF | Wood deck area |
| OpenPorchSF | Open porch area |
| EnclosedPorch | Enclosed porch area |
| 3SsnPorch | Three season porch area |
| ScreenPorch | Screen porch area |
| PoolArea | Pool area |
| MiscVal | Value of miscellaneous feature |
| MoSold | Month sold |
| YrSold | Year sold |

### Category C: Encoded Ordinal Features (KEPT: 12)

These are label-encoded categorical features that have inherent ordering (e.g., quality ratings).

| Feature | Original Feature | Encoding Type |
|---------|------------------|---------------|
| ExterQual_encoded | ExterQual | Label Encoding (ordinal) |
| ExterCond_encoded | ExterCond | Label Encoding (ordinal) |
| BsmtQual_encoded | BsmtQual | Label Encoding (ordinal) |
| BsmtCond_encoded | BsmtCond | Label Encoding (ordinal) |
| BsmtExposure_encoded | BsmtExposure | Label Encoding (ordinal) |
| BsmtFinType1_encoded | BsmtFinType1 | Label Encoding (ordinal) |
| BsmtFinType2_encoded | BsmtFinType2 | Label Encoding (ordinal) |
| HeatingQC_encoded | HeatingQC | Label Encoding (ordinal) |
| KitchenQual_encoded | KitchenQual | Label Encoding (ordinal) |
| FireplaceQu_encoded | FireplaceQu | Label Encoding (ordinal) |
| GarageQual_encoded | GarageQual | Label Encoding (ordinal) |
| GarageCond_encoded | GarageCond | Label Encoding (ordinal) |

### Category C: One-Hot Encoded Features (KEPT: 151)

These are one-hot encoded nominal categorical features (no inherent ordering).

**Feature Prefixes and Counts:**

| Original Feature | Encoded Columns | Count |
|------------------|-----------------|-------|
| BldgType | BldgType_2fmCon, BldgType_Duplex, BldgType_Twnhs... | 4 |
| CentralAir | CentralAir_Y | 1 |
| Condition1 | Condition1_Feedr, Condition1_Norm, Condition1_PosA... | 8 |
| Condition2 | Condition2_Feedr, Condition2_Norm, Condition2_PosA... | 7 |
| Electrical | Electrical_FuseF, Electrical_FuseP, Electrical_Mix... | 4 |
| Exterior1st | Exterior1st_AsphShn, Exterior1st_BrkComm, Exterior1st_BrkFace... | 14 |
| Exterior2nd | Exterior2nd_AsphShn, Exterior2nd_Brk Cmn, Exterior2nd_BrkFace... | 15 |
| Foundation | Foundation_CBlock, Foundation_PConc, Foundation_Slab... | 5 |
| Functional | Functional_Maj2, Functional_Min1, Functional_Min2... | 6 |
| GarageFinish | GarageFinish_RFn, GarageFinish_Unf | 2 |
| GarageType | GarageType_Attchd, GarageType_Basment, GarageType_BuiltIn... | 5 |
| Heating | Heating_GasA, Heating_GasW, Heating_Grav... | 5 |
| HouseStyle | HouseStyle_1.5Unf, HouseStyle_1Story, HouseStyle_2.5Fin... | 7 |
| LandContour | LandContour_HLS, LandContour_Low, LandContour_Lvl | 3 |
| LandSlope | LandSlope_Mod, LandSlope_Sev | 2 |
| LotConfig | LotConfig_CulDSac, LotConfig_FR2, LotConfig_FR3... | 4 |
| LotShape | LotShape_IR2, LotShape_IR3, LotShape_Reg | 3 |
| MSZoning | MSZoning_FV, MSZoning_RH, MSZoning_RL... | 4 |
| Neighborhood | Neighborhood_Blueste, Neighborhood_BrDale, Neighborhood_BrkSide... | 24 |
| PavedDrive | PavedDrive_P, PavedDrive_Y | 2 |
| RoofMatl | RoofMatl_Membran, RoofMatl_Metal, RoofMatl_Roll... | 6 |
| RoofStyle | RoofStyle_Gable, RoofStyle_Gambrel, RoofStyle_Hip... | 5 |
| SaleCondition | SaleCondition_AdjLand, SaleCondition_Alloca, SaleCondition_Family... | 5 |
| SaleType | SaleType_CWD, SaleType_Con, SaleType_ConLD... | 8 |
| Street | Street_Pave | 1 |
| Utilities | Utilities_NoSeWa | 1 |

### Category B: Engineered Features (REMOVED: 10)

These features were created through feature engineering and are removed in the minimal FE dataset.

| Feature | Type | Formula/Logic | Reason for Removal |
|---------|------|---------------|---------------------|
| TotalSF | Aggregation | Aggregation: TotalBsmtSF + 1stFlrSF + 2ndFlrSF | Combines multiple raw area features; tree models can learn this |
| HouseAge | Derived Metric | Derived metric: 2024 - YearBuilt | Derived from YearBuilt; linear transformation |
| YearsSinceRemod | Derived Metric | Derived metric: 2024 - YearRemodAdd | Derived from YearRemodAdd; linear transformation |
| TotalBathrooms | Aggregation | Aggregation: FullBath + 0.5*HalfBath + BsmtFullBath + 0.5*BsmtHalfBath | Weighted sum of bathroom features; tree models can aggregate |
| OverallScore | Composite Indicator | Composite indicator: OverallQual × OverallCond | Product of quality and condition; interaction term |
| TotalPorchSF | Aggregation | Aggregation: OpenPorchSF + EnclosedPorch + 3SsnPorch + ScreenPorch | Sum of porch areas; tree models can aggregate |
| HasGarage | Binary Indicator | Binary indicator: derived from GarageArea | Binary threshold on GarageArea; tree models can learn threshold |
| HasBasement | Binary Indicator | Binary indicator: derived from TotalBsmtSF | Binary threshold on TotalBsmtSF; tree models can learn threshold |
| HasFireplace | Binary Indicator | Binary indicator: derived from Fireplaces | Binary threshold on Fireplaces; tree models can learn threshold |
| IsRemodeled | Binary Indicator | Binary indicator: derived from YearBuilt vs YearRemodAdd | Comparison of two year features; tree models can learn comparison |

## Impact Analysis Framework

### Step 1: Train Models on Both Datasets

Train each model on:
1. Full FE Dataset (`processed_data.csv`)
2. Minimal FE Dataset (`processed_data_minimal_fe.csv`)

Models to test:
- Linear Regression
- Random Forest
- XGBoost

### Step 2: Calculate Performance Metrics

For each model and dataset combination, record:

**Regression Task:**
- RMSE (lower is better)
- R² (higher is better)
- MAE (lower is better)

**Classification Task:**
- Overall Accuracy
- Per-class Precision, Recall, F1

### Step 3: Compute Feature Engineering Impact Score

For each model, calculate:

```
FE_Impact_Score = ((Metric_Full_FE - Metric_Minimal_FE) / Metric_Full_FE) × 100%
```

**Interpretation:**
- **Positive score:** Model performs better with feature engineering
- **Negative score:** Model performs worse with feature engineering (rare)
- **Zero score:** No impact from feature engineering
- **Higher absolute value:** Greater dependence on feature engineering

### Step 4: Comparative Analysis

Compare FE Impact Scores across models to determine:

1. **Which model benefits MOST from feature engineering?**
   - Expected: Linear Regression

2. **Which model is MOST robust without feature engineering?**
   - Expected: XGBoost or Random Forest

3. **Does model ranking change between datasets?**
   - Current on Full FE: Linear > XGBoost > Random Forest
   - Expected on Minimal FE: XGBoost > Random Forest > Linear

## Expected Outcomes

### Hypothesis Confirmation Criteria

The hypothesis that "Feature Engineering disproportionately benefits Linear Regression" is confirmed if:

1. **Linear Regression FE Impact Score > XGBoost FE Impact Score**
   - Linear model shows larger performance drop without FE

2. **Linear Regression FE Impact Score > Random Forest FE Impact Score**
   - Linear model shows larger performance drop without FE

3. **Model Ranking Changes**
   - Full FE: Linear #1
   - Minimal FE: Linear NOT #1 (falls to #2 or #3)

### Alternative Outcomes

**Scenario A: All models benefit equally**
- All FE Impact Scores similar
- Suggests: Feature engineering provides universal benefit
- Implication: Continue using full FE for all models

**Scenario B: Tree models benefit more**
- XGBoost/RF Impact Scores > Linear Impact Score
- Suggests: Tree models also benefit from pre-computed features
- Implication: Feature engineering helps all models, not just linear

**Scenario C: Hypothesis confirmed**
- Linear Impact Score >> Tree-based Impact Scores
- Suggests: Linear models need FE, tree models don't
- Implication: Can use simpler features for tree-based models in production

## Next Steps

1. [x] **COMPLETED:** Feature audit and minimal FE dataset creation
2. [ ] **TODO:** Train Linear Regression on `processed_data_minimal_fe.csv`
3. [ ] **TODO:** Train Random Forest on `processed_data_minimal_fe.csv`
4. [ ] **TODO:** Train XGBoost on `processed_data_minimal_fe.csv`
5. [ ] **TODO:** Compare results between full FE and minimal FE datasets
6. [ ] **TODO:** Generate comparative analysis report with FE Impact Scores
7. [ ] **TODO:** Draw conclusions about Feature Engineering impact per model

## Files Generated

| File | Description | Features |
|------|-------------|----------|
| `processed_data.csv` | Full FE dataset (existing) | 209 |
| `processed_data_minimal_fe.csv` | Minimal FE dataset (new) | 199 |
| `FEATURE_ENGINEERING_AUDIT.md` | This audit report | - |

## Conclusion

This audit successfully identified and removed 10 engineered features from the processed dataset,
creating a controlled experimental setup to measure the impact of feature engineering on model performance.

The minimal FE dataset preserves all raw information and categorical encodings while removing
aggregations, derived metrics, and composite indicators that might disproportionately benefit certain models.

The experimental framework is now ready for model training and comparative analysis.

---
*Generated on 2026-06-13 at 11:04:24*