# XGBoost Training Summary Report

**Author:** pooya jafarpour  
**Date:** June 13, 2026  
**Dataset:** Ames Housing Dataset (Preprocessed)  
**Purpose:** Rigorous comparison of XGBoost against Linear Regression and Random Forest

---

## Executive Summary

XGBoost regression model was trained and evaluated using **identical preprocessing, train/test split, and evaluation metrics** as the existing Linear Regression and Random Forest models. The goal was to determine if XGBoost provides superior generalization performance.

**Key Finding:** XGBoost achieves **comparable performance** to Linear Regression, with all three models clustered within a narrow performance range. Linear Regression remains the best choice for deployment due to its **simplicity, interpretability, and minimal overfitting**.

---

## Model Comparison

### Performance Metrics

| Metric      | Linear Regression | Random Forest | XGBoost     |
|-------------|-------------------|---------------|-------------|
| **Test RMSE** | **$22,974.15**    | $23,133.58    | $23,072.61  |
| **Test R²**   | **0.8994**        | 0.8980        | 0.8986      |

**Performance Ranking (by Test RMSE):**
1. 🥇 **Linear Regression** - $22,974.15
2. 🥈 **XGBoost** - $23,072.61 (worse by $98.46)
3. 🥉 **Random Forest** - $23,133.58 (worse by $159.43)

### Interpretation

- **Performance differences are minimal** (~0.4% between best and worst)
- All models explain approximately **90% of price variance** (R² ≈ 0.90)
- Average prediction error is about **12.8% of mean house price** ($180,151)

---

## XGBoost Detailed Results

### Training Configuration

```python
XGBRegressor(
    n_estimators=100,      # 100 boosting rounds
    max_depth=6,           # Maximum tree depth
    learning_rate=0.1,     # Step size shrinkage
    random_state=42        # Reproducibility
)
```

### Performance Metrics

| Dataset  | RMSE        | R²     |
|----------|-------------|--------|
| Training | $4,188.10   | 0.9971 |
| Testing  | $23,072.61  | 0.8986 |

**Gap Analysis:**
- Train-Test RMSE Gap: **$18,884.51**
- Train-Test R² Gap: **0.0985**

---

## Top 20 Most Important Features

XGBoost feature importance analysis reveals the key drivers of housing prices:

| Rank | Feature                  | Importance Score |
|------|--------------------------|------------------|
| 1    | **OverallQual**          | **0.3480**       |
| 2    | **TotalSF**              | **0.1957**       |
| 3    | GarageCars               | 0.0292           |
| 4    | CentralAir_Y             | 0.0244           |
| 5    | OverallScore             | 0.0231           |
| 6    | BsmtQual_encoded         | 0.0208           |
| 7    | KitchenAbvGr             | 0.0203           |
| 8    | TotalBathrooms           | 0.0200           |
| 9    | ExterQual_encoded        | 0.0196           |
| 10   | GarageFinish_Unf         | 0.0123           |
| 11   | YearBuilt                | 0.0123           |
| 12   | TotRmsAbvGrd             | 0.0119           |
| 13   | KitchenQual_encoded      | 0.0099           |
| 14   | MSZoning_RM              | 0.0091           |
| 15   | Functional_Min1          | 0.0090           |
| 16   | Fireplaces               | 0.0078           |
| 17   | SaleType_New             | 0.0072           |
| 18   | YearRemodAdd             | 0.0071           |
| 19   | LotShape_Reg             | 0.0070           |
| 20   | GarageArea               | 0.0063           |

**Key Insights:**
- **OverallQual** (overall quality rating) dominates with 34.8% importance
- **TotalSF** (total square footage) is the second most important at 19.6%
- Top 2 features account for **54.4%** of total predictive power
- Garage features (cars, finish, area) appear multiple times in top 20
- Quality encodings (basement, exterior, kitchen) are highly influential

---

## Technical Analysis

### 1. Bias-Variance Trade-off

#### Linear Regression (High Bias, Low Variance)
- **Characteristics:** Simple linear assumptions, limited learning capacity
- **Strengths:** Excellent generalization, minimal overfitting
- **Weaknesses:** Cannot capture non-linear relationships or feature interactions
- **Test Performance:** R² = 0.8994 (BEST)

#### Random Forest (Lower Bias, Higher Variance)
- **Characteristics:** Ensemble of 100 decision trees with averaging
- **Strengths:** Captures non-linearities and feature interactions, robust to outliers
- **Weaknesses:** Risk of overfitting with deep trees (mitigated by ensemble averaging)
- **Test Performance:** R² = 0.8980

#### XGBoost (Balanced Bias-Variance)
- **Characteristics:** Sequential boosting with error correction and regularization
- **Strengths:** Sophisticated pattern learning, built-in regularization
- **Weaknesses:** Can overfit if not properly tuned
- **Test Performance:** R² = 0.8986

---

### 2. Overfitting Analysis

#### XGBoost Overfitting Indicators

⚠️ **SIGNIFICANT OVERFITTING DETECTED**

| Metric | Training | Testing | Gap      |
|--------|----------|---------|----------|
| RMSE   | $4,188   | $23,073 | $18,885  |
| R²     | 0.9971   | 0.8986  | 0.0985   |

**Analysis:**
- Training R² (99.71%) significantly exceeds Test R² (89.86%)
- Model memorizes training patterns that don't generalize well
- Large train-test gap indicates the model is too complex for this dataset

**Implications:**
- Baseline parameters (max_depth=6, learning_rate=0.1) allow excessive memorization
- Despite overfitting, test performance remains competitive with simpler models
- Further regularization could improve generalization

#### Comparison Across Models

```
Overfitting Severity (Train R² - Test R²):
- XGBoost:           0.0985 (HIGH - significant memorization)
- Random Forest:     ~0.08  (MODERATE - some memorization)
- Linear Regression: ~0.00  (MINIMAL - excellent generalization)
```

---

### 3. Why XGBoost Doesn't Outperform

Despite being a sophisticated algorithm, XGBoost performs **comparably** rather than **superior** to simpler models. Here's why:

#### Possible Explanations

1. **Dataset Characteristics**
   - Housing price relationships may be relatively **linear** in this dataset
   - Simple additive effects dominate over complex interactions
   - Limited benefit from non-linear modeling capacity

2. **Feature Engineering Quality**
   - Preprocessing already created effective features (TotalSF, OverallScore, etc.)
   - Encoded categorical variables capture most information
   - Little room for complex models to add value

3. **Sample Size Limitations**
   - Only 1,456 samples (1,164 training samples)
   - Complex models need more data to demonstrate advantages
   - Simpler models may be better suited for modest datasets

4. **Baseline Parameters**
   - No hyperparameter tuning performed (by design)
   - Default parameters may not be optimal for this specific dataset
   - Hyperparameter optimization could unlock better performance

5. **Overfitting Trade-off**
   - XGBoost's flexibility causes overfitting on training data
   - Regularization helps but limits learning capacity
   - Simpler models avoid this trade-off entirely

---

## Model Selection Recommendations

### ✅ **RECOMMENDATION: Deploy Linear Regression**

#### Rationale

1. **Best Test Performance**
   - Lowest Test RMSE: $22,974.15
   - Highest Test R²: 0.8994
   - Outperforms XGBoost by $98.46 and Random Forest by $159.43

2. **Minimal Overfitting**
   - Excellent generalization (Train R² ≈ Test R²)
   - No memorization of training noise
   - Stable predictions on unseen data

3. **Simplicity & Interpretability**
   - Transparent coefficients show feature relationships
   - Easy to explain to stakeholders
   - Fast training and inference
   - Lower maintenance overhead

4. **Computational Efficiency**
   - Instant training (milliseconds vs seconds)
   - Minimal memory footprint
   - No hyperparameters to tune

5. **Robustness**
   - Less prone to overfitting as dataset evolves
   - Stable performance across different data distributions

### Alternative Scenarios

**When to Consider XGBoost:**
- After hyperparameter tuning (GridSearchCV, Bayesian optimization)
- With larger datasets (>5,000 samples)
- When non-linear patterns become evident
- If interpretability is less critical than marginal accuracy gains

**When to Consider Random Forest:**
- Need feature importance with less overfitting than XGBoost
- Require robust predictions with minimal tuning
- Want ensemble diversity benefits

---

## Next Steps & Future Work

### 1. Hyperparameter Tuning (Optional)

If pursuing XGBoost optimization:

```python
# Reduce overfitting through regularization
XGBRegressor(
    n_estimators=200,          # More trees, lower learning rate
    max_depth=3,               # Shallower trees → less memorization
    learning_rate=0.05,        # Slower learning → better generalization
    subsample=0.8,             # Row sampling → reduce variance
    colsample_bytree=0.8,      # Column sampling → reduce correlation
    reg_alpha=0.1,             # L1 regularization
    reg_lambda=1.0,            # L2 regularization
    random_state=42
)
```

### 2. Cross-Validation

- Implement 5-fold or 10-fold cross-validation
- Obtain more robust performance estimates
- Reduce dependence on single train-test split

### 3. Ensemble Stacking

- Combine Linear Regression, Random Forest, and XGBoost predictions
- Meta-learner could leverage strengths of each approach

### 4. Feature Engineering

- Create additional interaction terms
- Explore polynomial features
- Engineer domain-specific features (price per square foot, age indicators)

### 5. Error Analysis

- Identify houses with largest prediction errors
- Investigate systematic biases (luxury homes, extreme conditions)
- Refine preprocessing or feature engineering accordingly

---

## Conclusions

1. **All three models achieve similar performance** (~90% R²), indicating the dataset may have inherently linear relationships or excellent feature engineering.

2. **Linear Regression wins** due to best test performance, minimal overfitting, and superior simplicity/interpretability trade-offs.

3. **XGBoost shows significant overfitting** (Train R² = 99.71% vs Test R² = 89.86%), suggesting baseline parameters are too permissive for this dataset size.

4. **Feature importance analysis** confirms **OverallQual** (34.8%) and **TotalSF** (19.6%) are dominant price drivers, with top 2 features explaining >50% of variance.

5. **No strong evidence** that complex non-linear modeling provides meaningful benefits over linear approaches for this housing dataset.

6. **Recommendation:** Deploy **Linear Regression** for production due to best test performance, excellent generalization, interpretability, and operational simplicity.

---

## Reproducibility

### Environment
- Python 3.13
- scikit-learn (LinearRegression, RandomForestRegressor)
- XGBoost 3.2.0
- Pandas, NumPy

### Data Split
- Test size: 20% (292 samples)
- Train size: 80% (1,164 samples)
- Random state: 42 (reproducible splits)

### Preprocessing
- Missing values: Filled with column means (348 values imputed)
- Features: 209 numerical/encoded features
- Target: SalePrice (continuous, $34,900 - $625,000)

---

**End of Report**
