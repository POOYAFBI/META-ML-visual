# Feature Engineering Impact Experiment

## Overview

This directory contains a controlled experiment to measure the impact of Feature Engineering on different machine learning models (Linear Regression, Random Forest, XGBoost).

## Experimental Setup

### Research Question
**Does Feature Engineering disproportionately benefit Linear Regression compared to tree-based models?**

### Hypothesis
Feature Engineering benefits Linear Regression more than tree-based models because:
1. Linear models cannot create non-linear interactions automatically
2. Engineered features provide explicit non-linear relationships
3. Tree-based models can discover these patterns naturally through splits

### Datasets

#### Dataset A: Full Feature Engineering
- **File:** `processed_data.csv`
- **Features:** 209
- **Includes:** 
  - 36 raw numerical features
  - 163 encoded categorical features (12 ordinal + 151 one-hot)
  - 10 engineered features

#### Dataset B: Minimal Feature Engineering
- **File:** `processed_data_minimal_fe.csv`
- **Features:** 199
- **Includes:**
  - 36 raw numerical features
  - 163 encoded categorical features (12 ordinal + 151 one-hot)
  - **NO engineered features**

### Removed Engineered Features (10 total)

| Feature | Type | Description |
|---------|------|-------------|
| TotalSF | Aggregation | Sum of all floor areas |
| HouseAge | Derived | 2024 - YearBuilt |
| YearsSinceRemod | Derived | 2024 - YearRemodAdd |
| TotalBathrooms | Aggregation | Weighted sum of bathrooms |
| OverallScore | Composite | OverallQual × OverallCond |
| TotalPorchSF | Aggregation | Sum of all porch areas |
| HasGarage | Binary | Threshold on GarageArea |
| HasBasement | Binary | Threshold on TotalBsmtSF |
| HasFireplace | Binary | Threshold on Fireplaces |
| IsRemodeled | Binary | YearBuilt ≠ YearRemodAdd |

## Files in This Directory

### Data Files
- `train.csv` - Original training data
- `test.csv` - Original test data
- `cleaned_data.csv` - After data cleaning
- `processed_data.csv` - Full FE dataset (209 features)
- `processed_data_minimal_fe.csv` - Minimal FE dataset (199 features)

### Scripts
- `preprocess_housing.py` - Original preprocessing with full FE
- `create_minimal_fe_dataset.py` - Creates minimal FE dataset
- `train_linear.py` - Train Linear Regression
- `train_rf.py` - Train Random Forest
- `train_xgb.py` - Train XGBoost
- `compare_fe_impact.py` - Calculate FE impact scores

### Documentation
- `data_description.txt` - Original feature descriptions
- `feature_names.txt` - List of all features in full FE dataset
- `DATA_CLEANING_REPORT.md` - Data cleaning documentation
- `FEATURE_ENGINEERING_AUDIT.md` - Detailed feature audit
- `DATASET_COMPARISON_SUMMARY.md` - Quick reference guide
- `README_FE_EXPERIMENT.md` - This file

### Training Results (Full FE)
- `RF_TRAINING_SUMMARY.md` - Random Forest results
- `XGB_TRAINING_SUMMARY.md` - XGBoost results
- (Linear Regression results to be documented)

## Experimental Workflow

### Phase 1: Setup (COMPLETED ✓)
1. ✓ Created `processed_data.csv` with full feature engineering
2. ✓ Audited all 209 features
3. ✓ Identified 10 engineered features
4. ✓ Created `processed_data_minimal_fe.csv` without engineered features
5. ✓ Generated audit report

### Phase 2: Training on Full FE (PARTIALLY COMPLETED)
1. ✓ Train Random Forest on `processed_data.csv`
2. ✓ Train XGBoost on `processed_data.csv`
3. ⏳ Train Linear Regression on `processed_data.csv`

### Phase 3: Training on Minimal FE (TODO)
1. ⏳ Train Linear Regression on `processed_data_minimal_fe.csv`
2. ⏳ Train Random Forest on `processed_data_minimal_fe.csv`
3. ⏳ Train XGBoost on `processed_data_minimal_fe.csv`

### Phase 4: Analysis (TODO)
1. ⏳ Collect all performance metrics
2. ⏳ Run `compare_fe_impact.py` to calculate impact scores
3. ⏳ Generate `FE_IMPACT_ANALYSIS.md`
4. ⏳ Draw conclusions about FE impact

## How to Train Models on Minimal FE Dataset

### Option 1: Modify Existing Training Scripts

Edit your training scripts to use the minimal FE dataset:

```python
# Change this line:
df = pd.read_csv('processed_data.csv')

# To this:
df = pd.read_csv('processed_data_minimal_fe.csv')
```

### Option 2: Create New Training Scripts

Copy your existing scripts with new names:

```bash
copy train_linear.py train_linear_minimal_fe.py
copy train_rf.py train_rf_minimal_fe.py
copy train_xgb.py train_xgb_minimal_fe.py
```

Then update the data file path in each new script.

### Option 3: Command Line Parameter

Add a command-line parameter to your training scripts:

```python
import sys

# Default to full FE
data_file = 'processed_data.csv'
if len(sys.argv) > 1 and sys.argv[1] == '--minimal-fe':
    data_file = 'processed_data_minimal_fe.csv'

df = pd.read_csv(data_file)
```

Then run:
```bash
python train_linear.py --minimal-fe
```

## Calculating FE Impact Scores

After training all models on both datasets:

1. Open `compare_fe_impact.py`
2. Fill in the results dictionaries with actual metrics:
   - `full_fe_results` - from your full FE training summaries
   - `minimal_fe_results` - from your minimal FE training runs
3. Run the script:
   ```bash
   python compare_fe_impact.py
   ```
4. Review the generated `FE_IMPACT_ANALYSIS.md`

### FE Impact Score Formula

For metrics where lower is better (RMSE, MAE):
```
Impact = ((Minimal_FE_Metric - Full_FE_Metric) / Full_FE_Metric) × 100%
```

For metrics where higher is better (R², Accuracy, F1):
```
Impact = ((Full_FE_Metric - Minimal_FE_Metric) / Full_FE_Metric) × 100%
```

**Interpretation:**
- Positive score: Model performs worse without FE (depends on FE)
- Negative score: Model performs better without FE (rare)
- Higher absolute value: Greater dependence on feature engineering

## Expected Results

### Scenario: Hypothesis Confirmed
- **Linear Regression:** High FE impact score (~10-20%)
- **Random Forest:** Low FE impact score (~0-5%)
- **XGBoost:** Low FE impact score (~0-5%)
- **Model Ranking Change:** Linear falls from #1 to #2 or #3

### Scenario: Hypothesis Rejected
- All models show similar FE impact scores
- Model ranking remains unchanged
- Suggests FE benefits all models equally

## Key Insights

### Why This Experiment Matters

1. **Production Optimization:**
   - If tree models don't need FE, we can simplify the pipeline
   - Reduced feature count = faster training and inference
   - Less maintenance overhead

2. **Model Selection:**
   - Understand which models need manual feature engineering
   - Choose appropriate model based on available FE resources

3. **Feature Engineering ROI:**
   - Measure the return on investment for FE effort
   - Prioritize FE for models that benefit most

4. **Scientific Understanding:**
   - Empirical evidence of model behavior differences
   - Data-driven insights into model capabilities

## Notes

### What We Kept
- All raw numerical features (original data)
- All encoded categorical features (necessary transformations)
- Both targets (SalePrice, price_class)

### What We Removed
- Only hand-crafted engineered features
- Features that combine multiple raw features
- Features that represent derived calculations
- Binary indicators based on thresholds

### What This Controls For
- Same data samples (1456 rows)
- Same target variables
- Same data types and encoding
- Only difference: presence/absence of 10 engineered features

## Questions to Answer

1. Which model benefits MOST from feature engineering?
2. Which model is MOST robust without feature engineering?
3. Does model ranking change between datasets?
4. What is the magnitude of FE impact for each model?
5. Should we continue using FE for tree-based models in production?

## Contact & Contributions

This experiment is designed to be reproducible and transparent. All scripts, data, and results are documented for verification.

---

**Experiment Status:** Phase 1 Complete, Phase 2 Partial, Phases 3-4 Pending  
**Last Updated:** 2026-06-13  
**Data Scientist:** ML Team
