# 🏠 Housing Price Prediction - ML Benchmarking Project -demo

A comprehensive machine learning project comparing regression and classification models for housing price prediction using the Ames Housing Dataset.
this is expermental and in early stages only for experemts.
full version will be updated and uploaded in another repo and will receive updates for new ml models and ux - ui
read the expermental md files to found out what really happend in the background of making this and enjoy!!

---

## 📁 Project Structure

```
P/
├── 📊 data/                    # All datasets
├── 🚂 training/                # Model training scripts (regression)
├── 🧪 experiments/             # Feature engineering experiments
├── 📄 reports/                 # Analysis and documentation
├── 📈 results/                 # Model outputs (JSON)
├── 🛠️ utils/                   # Preprocessing utilities
└── 🎯 classification_experiment/  # Classification experiments
    ├── training/              # Classification model scripts
    ├── experiments/           # Classification utilities
    ├── reports/               # Classification documentation
    └── results/               # Classification outputs
```

---

## 🚀 Quick Start

### 1. Data Preprocessing (First Time Only)

```bash
cd utils
python preprocess_housing.py
```

**Generates:**
- `data/cleaned_data.csv` - Cleaned raw data
- `data/processed_data.csv` - Processed features for modeling

### 2. Regression Training

```bash
cd training

# Linear Regression
python train_linear.py

# Random Forest
python train_rf.py

# XGBoost
python train_xgb.py
```

### 3. Classification Training

```bash
cd classification_experiment/training

# Logistic Regression
python train_logistic.py

# Random Forest Classifier
python train_random_forest.py

# XGBoost Classifier
python train_xgboost.py
```

### 4. Feature Engineering Experiments

```bash
cd experiments

# Create minimal feature engineering dataset
python create_minimal_fe_dataset.py

# Compare feature engineering impact
python compare_fe_impact.py
```

---

## 📊 Available Datasets

Located in `data/` directory:

| Dataset | Description | Features | Use Case |
|---------|-------------|----------|----------|
| `train.csv` | Raw Kaggle training data | 81 | Initial import |
| `cleaned_data.csv` | Cleaned dataset | 81 | After cleaning |
| `processed_data.csv` | Fully processed dataset | 209 | Standard training |
| `processed_data_minimal_fe.csv` | Reduced feature engineering | 199 | FE impact study |
| `processed_data_classification_fe.csv` | Classification-specific FE | 212 | Classification models |

---

## 🎯 Model Performance Summary

### Regression Models (RMSE on Test Set)

| Model | Standard Dataset | Minimal FE Dataset |
|-------|------------------|-------------------|
| Linear Regression | $22,974.15 | TBD |
| Random Forest | $23,133.58 | TBD |
| XGBoost | ~$23,000 | TBD |

### Classification Models (F1-Score Macro on Test Set)

| Model | Baseline | Enhanced FE |
|-------|----------|-------------|
| Logistic Regression | TBD | TBD |
| Random Forest | TBD | TBD |
| XGBoost | TBD | TBD |

---

## 📚 Key Reports

### Regression Analysis
- `reports/FINAL_RESULTS_COMPARISON.md` - Complete regression model comparison
- `reports/FE_IMPACT_ANALYSIS.md` - Feature engineering impact study
- `reports/DATA_CLEANING_REPORT.md` - Data preprocessing details

### Classification Analysis
- `classification_experiment/reports/EXECUTIVE_SUMMARY.md` - Classification overview
- `classification_experiment/reports/CLASSIFICATION_RESULTS_REPORT.md` - Detailed results
- `classification_experiment/reports/EXPERIMENT_ANSWERS.md` - Key findings

---

## 🛠️ Technical Stack

- **Language:** Python 3.x
- **Core Libraries:**
  - `pandas` - Data manipulation
  - `numpy` - Numerical operations
  - `scikit-learn` - ML models and preprocessing
  - `xgboost` - Gradient boosting
- **Data:** Ames Housing Dataset

---

## 🔄 Typical Workflow

1. **Initial Setup:**
   ```bash
   # Preprocess raw data
   cd utils && python preprocess_housing.py
   ```

2. **Baseline Models:**
   ```bash
   # Train all regression models
   cd ../training
   python train_linear.py
   python train_rf.py
   python train_xgb.py
   ```

3. **Classification Experiments:**
   ```bash
   # Apply feature engineering
   cd ../classification_experiment/experiments
   python apply_feature_engineering.py
   
   # Train classification models
   cd ../training
   python train_logistic.py
   python train_random_forest.py
   python train_xgboost.py
   ```

4. **Analysis:**
   - Check `reports/` for regression analysis
   - Check `classification_experiment/reports/` for classification analysis

---

## 📈 Model Training Details

### Regression Target
- **Variable:** `SalePrice` (continuous)
- **Range:** ~$34,900 - $755,000
- **Metric:** RMSE (Root Mean Square Error), R²

### Classification Target
- **Variable:** `price_class` (categorical)
- **Classes:** 
  - 0 = Low price
  - 1 = Medium price
  - 2 = High price
- **Metric:** F1-Score (macro), Accuracy

---

## 🧪 Experiment Types

### 1. Baseline Comparison
Compare Linear Regression, Random Forest, and XGBoost on standard dataset.

### 2. Feature Engineering Impact
Measure performance difference between:
- Full feature engineering (209 features)
- Minimal feature engineering (199 features)

### 3. Classification Performance
Evaluate classification models with:
- Baseline features
- Enhanced features (interaction terms, log transforms, class boundary refinement)

---

## 📝 File Naming Conventions

- `train_*.py` - Model training scripts
- `*_results.json` - Model output metrics
- `*_enhanced.py` - Scripts using enhanced features
- `*_minimal_fe.py` - Scripts using minimal feature engineering
- `processed_data*.csv` - Processed datasets
- `*_SUMMARY.md` - High-level reports
- `*_REPORT.md` - Detailed analysis

---

## 🚨 Important Notes

1. **Always run from the script's directory** - Scripts use relative paths
2. **Data files are in `data/`** - All scripts reference `../data/` or `../../data/`
3. **Results auto-save** - JSON files save to `results/` or `../results/`
4. **No manual path editing needed** - All paths are configured correctly

---

## 🔍 Troubleshooting

### "File not found" errors
- Ensure you're running scripts from their directory (e.g., `cd training` then `python train_linear.py`)
- Verify `data/processed_data.csv` exists (run `utils/preprocess_housing.py` first)

### Missing dependencies
```bash
pip install pandas numpy scikit-learn xgboost
```

### Results not saving
- Check that `results/` or `classification_experiment/results/` directory exists
- Verify write permissions

---

## 📖 Further Reading

- **Refactoring Details:** See `REFACTORING_SUMMARY.md`
- **Classification Quickstart:** See `classification_experiment/reports/00_START_HERE.md`
- **Feature Engineering:** See `classification_experiment/reports/FEATURE_ENGINEERING_REPORT.md`

---

## 👥 Contributing

When adding new experiments or models:
1. Place training scripts in `training/` or `classification_experiment/training/`
2. Place analysis scripts in `experiments/` or `classification_experiment/experiments/`
3. Save results to `results/` or `classification_experiment/results/`
4. Document findings in `reports/` or `classification_experiment/reports/`

---

**Project Status:** ✅ Refactored and production-ready  
**Last Updated:** June 13, 2026
