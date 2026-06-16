# Classification Experiment Workspace

**Purpose:** Multi-model classification benchmarking on Dataset A (Ames Housing)  
**Date:** June 13, 2026  
**Status:** ✅ COMPLETE

---

## Overview

This workspace contains a complete classification experiment comparing three machine learning models:

1. **Logistic Regression** - Linear baseline classifier
2. **Random Forest** - Tree-based ensemble classifier
3. **XGBoost** - Gradient boosting classifier

**Objective:** Identify the best model for classifying house prices into three categories (Low, Medium, High) based on F1-macro score.

**Result:** Random Forest wins with F1-macro score of 0.8455

---

## Directory Structure

```
classification_experiment/
│
├── README.md                              # This file
├── CLASSIFICATION_RESULTS_REPORT.md       # Comprehensive analysis report
│
├── train_logistic.py                      # Logistic Regression training
├── train_random_forest.py                 # Random Forest training
├── train_xgboost.py                       # XGBoost training
│
├── logistic_results.json                  # LR metrics
├── random_forest_results.json             # RF metrics
└── xgboost_results.json                   # XGB metrics
```

---

## Quick Start

### 1. Train All Models

```bash
# Train Logistic Regression
python train_logistic.py

# Train Random Forest
python train_random_forest.py

# Train XGBoost
python train_xgboost.py
```

### 2. View Results

All results are saved in JSON format and printed to console during training.

See `CLASSIFICATION_RESULTS_REPORT.md` for complete analysis.

---

## Dataset Information

**Source:** Dataset A (processed_data.csv in parent directory)  
**Samples:** 1,456 houses  
**Features:** 209 (after preprocessing)  
**Target:** price_class (0=low, 1=medium, 2=high)  

**Class Distribution:**
- Low: 483 samples (33.2%)
- Medium: 478 samples (32.8%)
- High: 495 samples (34.0%)

**Split:**
- Training: 1,164 samples (80%)
- Test: 292 samples (20%)
- Stratified: Yes (maintains class balance)

---

## Model Performance Summary

| Model | F1-Macro | Accuracy | Status |
|-------|----------|----------|--------|
| **Random Forest** | **0.8455** ⭐ | 84.59% | Winner |
| XGBoost | 0.8315 | 83.22% | Strong |
| Logistic Regression | 0.7964 | 79.79% | Baseline |

---

## Key Findings

1. **Random Forest achieves best F1-macro score (0.8455)**
2. **Non-linear models outperform linear baseline by ~5-6%**
3. **All models struggle with medium-price class** (boundary region)
4. **TotalSF (total square footage) is most important feature**
5. **Tree models show overfitting** (perfect training accuracy)

---

## Experimental Design

### Consistent Across All Models

- ✅ Same dataset (Dataset A)
- ✅ Same random seed (random_state=42)
- ✅ Same train/test split (80/20, stratified)
- ✅ Same preprocessing (median imputation for NaN)
- ✅ Proper scaling (StandardScaler for Logistic Regression only)

### Primary Metric

**F1-Macro Score** - Unweighted average of per-class F1 scores

Why F1-Macro?
- Treats all classes equally (no bias toward majority)
- Balances precision and recall
- Better than accuracy for multi-class problems

### Secondary Metrics

- Accuracy
- Per-class F1 scores
- Confusion matrix
- Precision and Recall

---

## Reproduction Instructions

### Prerequisites

```bash
pip install pandas numpy scikit-learn xgboost
```

### Reproduce Results

```bash
cd classification_experiment
python train_logistic.py        # ~30 seconds
python train_random_forest.py   # ~1-2 minutes
python train_xgboost.py         # ~1-2 minutes
```

All results are deterministic (random_state=42) and will match exactly.

---

## Comparison with Regression Experiment

**Interesting Finding:** Model rankings change between tasks!

| Task | Best | 2nd | 3rd |
|------|------|-----|-----|
| **Regression** | Linear Regression | XGBoost | Random Forest |
| **Classification** | Random Forest | XGBoost | Logistic Regression |

**Why?** Classification introduces hard decision boundaries that favor non-linear models, while regression allows smooth linear relationships.

---

## Production Recommendation

**Deploy:** Random Forest Classifier

**Configuration:**
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)
```

**Expected Performance:**
- F1-Macro: ~0.845
- Accuracy: ~84-85%
- Inference: Fast (parallel tree evaluation)

**Advantages:**
- Best performance
- No scaling required (simpler pipeline)
- Robust to outliers
- Feature importance available

---

## Future Improvements

1. **Hyperparameter Tuning**
   - GridSearchCV or RandomizedSearchCV
   - Could improve XGBoost to match/exceed RF

2. **Cross-Validation**
   - 5-fold or 10-fold CV
   - More robust performance estimates

3. **Feature Engineering**
   - Polynomial features for Logistic Regression
   - Feature selection to reduce overfitting

4. **Ensemble Methods**
   - Voting classifier
   - Stacking

5. **Address Overfitting**
   - Regularization
   - Reduce model complexity
   - More training data

---

## Contact & Context

This classification experiment is part of a larger project comparing model behavior across regression and classification tasks.

**Regression experiment:** Located in parent directory  
**Classification experiment:** This directory  
**Next step:** Unified analysis across both tasks

---

**Last Updated:** June 13, 2026  
**Status:** Production-ready results  
**Reproducibility:** 100% (fixed random seed)

