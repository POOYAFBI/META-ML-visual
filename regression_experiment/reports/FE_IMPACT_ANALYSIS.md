# Feature Engineering Impact Analysis

## Executive Summary

This report presents the results of a controlled experiment measuring the impact of Feature Engineering on three machine learning models: Linear Regression, Random Forest, and XGBoost.

**Date:** June 13, 2026  
**Experiment:** Full FE (209 features) vs Minimal FE (199 features)  
**Removed Features:** 10 engineered features

---

## Experimental Design

### Datasets

**Dataset A: Full Feature Engineering**
- File: `processed_data.csv`
- Features: 209
- Includes: 36 raw + 163 encoded + **10 engineered features**

**Dataset B: Minimal Feature Engineering**
- File: `processed_data_minimal_fe.csv`
- Features: 199
- Includes: 36 raw + 163 encoded + **0 engineered features**

### Removed Engineered Features (10)

1. **TotalSF** - Aggregation: TotalBsmtSF + 1stFlrSF + 2ndFlrSF
2. **HouseAge** - Derived: 2024 - YearBuilt
3. **YearsSinceRemod** - Derived: 2024 - YearRemodAdd
4. **TotalBathrooms** - Aggregation: Weighted sum of all bathrooms
5. **OverallScore** - Composite: OverallQual × OverallCond
6. **TotalPorchSF** - Aggregation: Sum of all porch areas
7. **HasGarage** - Binary: GarageArea > 0
8. **HasBasement** - Binary: TotalBsmtSF > 0
9. **HasFireplace** - Binary: Fireplaces > 0
10. **IsRemodeled** - Binary: YearBuilt ≠ YearRemodAdd

### Methodology

- **Train/Test Split:** 80/20 (test_size=0.2, random_state=42)
- **Models:** Same hyperparameters for both datasets
- **Metrics:** RMSE (lower is better), R² (higher is better)

---

## Performance Comparison

### Complete Results Table

| Model | Dataset | Test RMSE | Test R² | Train RMSE | Train R² |
|-------|---------|-----------|---------|------------|----------|
| **Linear Regression** | Full FE | $22,974.15 | 0.8994 | N/A | N/A |
| **Linear Regression** | Minimal FE | $23,239.24 | 0.8971 | $20,426.14 | 0.9308 |
| **Random Forest** | Full FE | $23,133.58 | 0.8980 | N/A | N/A |
| **Random Forest** | Minimal FE | $24,218.50 | 0.8882 | $9,871.03 | 0.9838 |
| **XGBoost** | Full FE | $23,072.84 | 0.8986 | N/A | N/A |
| **XGBoost** | Minimal FE | $24,618.88 | 0.8845 | $4,983.12 | 0.9959 |

---

## Feature Engineering Impact Scores

### Impact Calculation Formula

For RMSE (lower is better):
```
RMSE Impact % = ((Minimal_FE_RMSE - Full_FE_RMSE) / Full_FE_RMSE) × 100%
```

For R² (higher is better):
```
R² Impact % = ((Full_FE_R² - Minimal_FE_R²) / Full_FE_R²) × 100%
```

### Impact Scores by Model

| Model | RMSE Change | RMSE Impact % | R² Change | R² Impact % |
|-------|-------------|---------------|-----------|-------------|
| **Linear Regression** | +$265.09 | **+1.15%** | -0.0023 | **+0.26%** |
| **Random Forest** | +$1,084.92 | **+4.69%** | -0.0098 | **+1.09%** |
| **XGBoost** | +$1,546.04 | **+6.70%** | -0.0141 | **+1.57%** |

### Visual Ranking by FE Dependence

```
HIGHEST DEPENDENCE ON FEATURE ENGINEERING
↑
│  🥇 XGBoost         +6.70% RMSE impact
│  🥈 Random Forest   +4.69% RMSE impact  
│  🥉 Linear Reg      +1.15% RMSE impact
↓
LOWEST DEPENDENCE ON FEATURE ENGINEERING
```

---

## Model Rankings

### Full FE Dataset Performance

**By Test RMSE (lower is better):**

1. 🥇 **Linear Regression** - $22,974.15
2. 🥈 **XGBoost** - $23,072.84  
3. 🥉 **Random Forest** - $23,133.58

**By Test R² (higher is better):**

1. 🥇 **Linear Regression** - 0.8994
2. 🥈 **XGBoost** - 0.8986
3. 🥉 **Random Forest** - 0.8980

### Minimal FE Dataset Performance

**By Test RMSE (lower is better):**

1. 🥇 **Linear Regression** - $23,239.24
2. 🥈 **Random Forest** - $24,218.50
3. 🥉 **XGBoost** - $24,618.88

**By Test R² (higher is better):**

1. 🥇 **Linear Regression** - 0.8971
2. 🥈 **Random Forest** - 0.8882
3. 🥉 **XGBoost** - 0.8845

### Ranking Change Analysis

**DID THE RANKING CHANGE?**

📊 **PARTIAL CHANGE:**
- Linear Regression remained #1 on both datasets
- XGBoost and Random Forest **swapped positions**
  - Full FE: XGBoost (#2) > Random Forest (#3)
  - Minimal FE: Random Forest (#2) > XGBoost (#3)

**Interpretation:**
- Linear Regression's dominance persisted even without engineered features
- Tree-based models were more sensitive to FE removal
- XGBoost showed the largest performance degradation

---

## Hypothesis Testing

### Original Hypothesis

**"Feature Engineering disproportionately benefits Linear Regression compared to tree-based models."**

**Expected Results:**
- Linear Regression would show LARGEST performance drop
- Tree-based models would be ROBUST (minimal drop)
- Rationale: Linear models can't create interactions; tree models can

### Actual Results

**HYPOTHESIS REJECTED** ❌

**Evidence:**

1. **Impact Score Ranking:**
   - XGBoost: +6.70% RMSE impact (HIGHEST)
   - Random Forest: +4.69% RMSE impact (MIDDLE)
   - Linear Regression: +1.15% RMSE impact (LOWEST)

2. **Performance Drop:**
   - XGBoost degraded most: +$1,546 RMSE
   - Random Forest degraded moderately: +$1,085 RMSE
   - Linear Regression degraded least: +$265 RMSE

3. **Model Ranking:**
   - Linear Regression maintained #1 position
   - Tree-based models fell in ranking

### Why Was The Hypothesis Wrong?

**Finding:** The engineered features provided MORE value to tree-based models than to Linear Regression.

**Explanations:**

1. **Pre-Computation Efficiency**
   - Engineered features like `TotalSF` and `OverallScore` are pre-computed combinations
   - Tree models would need multiple splits to recreate these patterns
   - Having them pre-computed reduced the model's learning burden

2. **Feature Space Dimensionality**
   - Removing 10 features reduced tree models' ability to find optimal splits
   - Linear Regression uses all features simultaneously (dot product)
   - Trees select subset of features per split → more sensitive to feature removal

3. **Interaction Capture**
   - `OverallScore = OverallQual × OverallCond` captures a key interaction
   - XGBoost would need to learn this through multiple splits
   - Pre-computing this interaction accelerated tree learning

4. **Aggregation Features**
   - Features like `TotalBathrooms` aggregate multiple raw features
   - Trees must split on each bathroom type separately
   - Aggregated feature provides more direct signal

---

## Detailed Analysis by Model

### 1. Linear Regression

**Performance:**
- Full FE: RMSE $22,974.15, R² 0.8994
- Minimal FE: RMSE $23,239.24, R² 0.8971
- **Impact: +1.15% RMSE, +0.26% R²**

**Interpretation:**
- **MOST ROBUST** to feature engineering removal
- Maintained #1 ranking on both datasets
- Only $265 RMSE increase (1.15%)

**Why So Robust?**
1. **Linear Coefficients:** Uses all features simultaneously
2. **Mathematical Form:** y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ
3. **Redundancy Handling:** When TotalSF removed, model compensated with 1stFlrSF, 2ndFlrSF, TotalBsmtSF coefficients
4. **Least Squares:** Optimal fit given available features

**Conclusion:** Linear Regression does NOT heavily depend on feature engineering for this dataset.

---

### 2. Random Forest

**Performance:**
- Full FE: RMSE $23,133.58, R² 0.8980
- Minimal FE: RMSE $24,218.50, R² 0.8882
- **Impact: +4.69% RMSE, +1.09% R²**

**Interpretation:**
- **MODERATE DEPENDENCE** on feature engineering
- Fell from #3 to #2 (improved relative ranking)
- $1,085 RMSE increase (4.69%)

**Why Moderate Impact?**
1. **Ensemble Averaging:** 100 trees reduce variance, improve robustness
2. **Feature Bootstrapping:** Random feature selection at each split provides diversity
3. **But:** Pre-computed features like TotalSF provided more direct splits
4. **Overfitting Risk:** High training R² (0.9838) vs test R² (0.8882) suggests some overfitting

**Conclusion:** Random Forest benefits from engineered features but remains competitive without them.

---

### 3. XGBoost

**Performance:**
- Full FE: RMSE $23,072.84, R² 0.8986
- Minimal FE: RMSE $24,618.88, R² 0.8845
- **Impact: +6.70% RMSE, +1.57% R²**

**Interpretation:**
- **HIGHEST DEPENDENCE** on feature engineering
- Fell from #2 to #3 (worst relative ranking)
- $1,546 RMSE increase (6.70%)

**Why Highest Impact?**
1. **Sequential Learning:** XGBoost builds trees to correct previous errors
2. **Gradient-Based:** Optimizes for residual reduction
3. **Split Quality:** Pre-computed features (TotalSF, OverallScore) provided high-gain splits
4. **Feature Interaction:** Boosting relies on feature quality for error correction
5. **Severe Overfitting:** Training R² (0.9959) >> Test R² (0.8845) indicates memorization

**Top Feature Without FE:**
- OverallQual (0.4581 importance) - dominates feature importance
- Without OverallScore composite, relies heavily on individual quality rating

**Conclusion:** XGBoost HEAVILY depends on engineered features for optimal performance.

---

## Practical Implications

### 1. Production System Recommendations

**Scenario A: Maximum Accuracy Required**
- **Recommended Model:** Linear Regression on Full FE dataset
- **RMSE:** $22,974.15
- **Rationale:** Best absolute performance, stable across datasets

**Scenario B: Simple Feature Pipeline**
- **Recommended Model:** Linear Regression on Minimal FE dataset
- **RMSE:** $23,239.24 (only +$265 from best)
- **Rationale:** 1.15% accuracy trade-off for 10 fewer features

**Scenario C: Tree-Based Model Required**
- **Recommended Model:** Random Forest on Full FE dataset
- **RMSE:** $23,133.58
- **Warning:** Random Forest degrades 4.69%, XGBoost degrades 6.70% without FE
- **Rationale:** Tree models NEED engineered features for competitive performance

### 2. Feature Engineering ROI

**Investment vs Return:**

| Model | FE Effort (10 features) | Performance Gain | ROI |
|-------|------------------------|------------------|-----|
| Linear Regression | High | +1.15% | **Low ROI** |
| Random Forest | High | +4.69% | **Medium ROI** |
| XGBoost | High | +6.70% | **High ROI** |

**Recommendation:**
- **For Linear Models:** Minimal FE is sufficient
- **For Tree Models:** Invest in feature engineering

### 3. Model Selection Strategy

**If you have engineered features:**
- ✅ Use Linear Regression (best performance)
- ✅ XGBoost is competitive (#2)

**If you don't have engineered features:**
- ✅ Use Linear Regression (still best)
- ⚠️ Avoid XGBoost (largest degradation)
- ⚠️ Random Forest is acceptable (#2)

### 4. Production Pipeline Optimization

**Minimal FE Pipeline (Recommended):**
```
Raw Data → Encoding → Linear Regression
```
- **Pros:** Simple, maintainable, 98.85% of full FE performance
- **Cons:** Tree models perform worse

**Full FE Pipeline:**
```
Raw Data → Encoding → Feature Engineering (10 features) → Model
```
- **Pros:** Best tree-model performance
- **Cons:** More complex, more maintenance

---

## Scientific Insights

### Key Discoveries

1. **Counter-Intuitive Result:**
   - Tree-based models depend MORE on FE than Linear models
   - Contradicts common machine learning wisdom

2. **Pre-Computation Value:**
   - Engineered features save trees from learning complex patterns
   - Linear models compensate through coefficient adjustment

3. **Model Architecture Matters:**
   - Sequential learning (XGBoost) more sensitive than ensemble (Random Forest)
   - Linear models most robust to feature changes

4. **Interaction Terms:**
   - OverallScore (Quality × Condition) was highly valuable
   - XGBoost's feature importance showed OverallQual dominated (0.4581)

### Implications for ML Practice

1. **Don't Skip FE for Tree Models:**
   - Common advice: "Tree models don't need FE"
   - **This experiment shows: FALSE**

2. **Linear Models Are Robust:**
   - Despite inability to create interactions
   - Coefficient flexibility compensates well

3. **Feature Engineering Benefits All Models:**
   - But benefit magnitude varies by architecture
   - XGBoost benefits most, Linear least

---

## Conclusion

### Final Answer to Research Question

**"Does Feature Engineering disproportionately benefit Linear Regression?"**

**Answer:** **NO** ❌

**Evidence:**
- Linear Regression showed LEAST dependence (+1.15%)
- XGBoost showed HIGHEST dependence (+6.70%)
- Random Forest showed MODERATE dependence (+4.69%)

### The Real Story

**Feature Engineering disproportionately benefits TREE-BASED MODELS, especially XGBoost.**

Pre-computed aggregations, interactions, and derived features provide more value to gradient boosting and random forests than to linear models, which can compensate through coefficient adjustment.

### Production Recommendation

**For this housing price prediction task:**

🏆 **Best Choice:** Linear Regression on Minimal FE dataset
- RMSE: $23,239.24 (only 1.15% worse than full FE)
- Simplest feature pipeline
- Most robust to feature engineering choices
- Easiest to maintain and explain

**Alternative:** Linear Regression on Full FE dataset for absolute best accuracy ($22,974.15 RMSE)

**Avoid:** XGBoost on Minimal FE dataset (largest performance degradation)

---

## Lessons Learned

1. **Test Your Assumptions:** The hypothesis was reasonable but wrong
2. **Empirical Validation Matters:** Theory ≠ Practice
3. **Model Behavior is Data-Specific:** Results may vary on other datasets
4. **Simple Models Can Win:** Linear Regression outperformed complex models
5. **Feature Engineering ROI Varies:** Measure impact per model architecture

---

**Experiment Date:** June 13, 2026  
**Analysis By:** ML Team  
**Status:** Complete ✅  
**Reproducibility:** All code and data available
