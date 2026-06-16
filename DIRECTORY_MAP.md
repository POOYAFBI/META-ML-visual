# 🗺️ COMPLETE DIRECTORY MAP

**Project:** Machine Learning Housing Price Prediction  
**Last Updated:** June 13, 2026  
**Purpose:** Visual reference for file locations

---

## 📂 FULL DIRECTORY TREE

```
P/
│
├── 📄 README.md                              ← START HERE! Project overview
├── 📄 REFACTORING_SUMMARY.md                 ← Complete refactoring documentation
├── 📄 MIGRATION_CHECKLIST.md                 ← Verification checklist
├── 📄 DIRECTORY_MAP.md                       ← This file
│
├── 📊 data/                                  ← ALL DATASETS
│   ├── train.csv                            (Raw Kaggle training data)
│   ├── test.csv                             (Raw Kaggle test data)
│   ├── sample_submission.csv                (Submission format)
│   ├── cleaned_data.csv                     (Post-cleaning, pre-processing)
│   ├── processed_data.csv                   (Full FE, 209 features)
│   ├── processed_data_minimal_fe.csv        (Reduced FE, 199 features)
│   ├── processed_data_classification_fe.csv (Classification-specific, 212 features)
│   ├── data_description.txt                 (Feature descriptions from Kaggle)
│   └── feature_names.txt                    (List of engineered features)
│
├── 🚂 training/                              ← REGRESSION MODEL TRAINING
│   ├── train_linear.py                      (Linear Regression baseline)
│   ├── train_linear_minimal_fe.py           (Linear with reduced features)
│   ├── train_rf.py                          (Random Forest baseline)
│   ├── train_rf_minimal_fe.py               (Random Forest with reduced features)
│   ├── train_xgb.py                         (XGBoost baseline)
│   └── train_xgb_minimal_fe.py              (XGBoost with reduced features)
│
├── 🧪 experiments/                           ← FEATURE ENGINEERING EXPERIMENTS
│   ├── create_minimal_fe_dataset.py         (Generate reduced FE dataset)
│   └── compare_fe_impact.py                 (Analyze FE impact on performance)
│
├── 📄 reports/                               ← REGRESSION ANALYSIS & DOCS
│   ├── DATA_CLEANING_REPORT.md              (Data cleaning process)
│   ├── DATASET_COMPARISON_SUMMARY.md        (Dataset comparison analysis)
│   ├── EXPERIMENT_COMPLETE.md               (Experiment completion status)
│   ├── FE_IMPACT_ANALYSIS.md                (Feature engineering impact)
│   ├── FEATURE_ENGINEERING_AUDIT.md         (FE audit details)
│   ├── FINAL_RESULTS_COMPARISON.md          (Complete model comparison)
│   ├── LINEAR_MINIMAL_FE_SUMMARY.md         (Linear model minimal FE results)
│   ├── README_FE_EXPERIMENT.md              (FE experiment README)
│   ├── RF_MINIMAL_FE_SUMMARY.md             (Random Forest minimal FE results)
│   ├── RF_TRAINING_SUMMARY.md               (Random Forest training summary)
│   ├── XGB_MINIMAL_FE_SUMMARY.md            (XGBoost minimal FE results)
│   └── XGB_TRAINING_SUMMARY.md              (XGBoost training summary)
│
├── 📈 results/                               ← REGRESSION MODEL OUTPUTS
│   └── (Empty - ready for JSON outputs)
│
├── 🛠️ utils/                                 ← PREPROCESSING UTILITIES
│   └── preprocess_housing.py                (Data cleaning & feature engineering)
│
└── 🎯 classification_experiment/             ← CLASSIFICATION EXPERIMENTS
    │
    ├── data/                                 (Empty - uses parent data/)
    │
    ├── utils/                                (Empty - uses parent utils/)
    │
    ├── 🚂 training/                          ← CLASSIFICATION MODEL TRAINING
    │   ├── train_logistic.py                (Logistic Regression baseline)
    │   ├── train_logistic_enhanced.py       (Logistic with enhanced FE)
    │   ├── train_random_forest.py           (Random Forest Classifier baseline)
    │   ├── train_random_forest_enhanced.py  (Random Forest with enhanced FE)
    │   ├── train_xgboost.py                 (XGBoost Classifier baseline)
    │   └── train_xgboost_enhanced.py        (XGBoost with enhanced FE)
    │
    ├── 🧪 experiments/                       ← CLASSIFICATION UTILITIES
    │   ├── apply_feature_engineering.py     (Apply classification-specific FE)
    │   ├── check_data.py                    (Data validation)
    │   ├── compare_baseline_vs_enhanced.py  (Compare baseline vs enhanced)
    │   ├── compare_models.py                (Model comparison utility)
    │   ├── inspect_data.py                  (Data inspection tool)
    │   └── validate_transformed_data.py     (Validate transformed dataset)
    │
    ├── 📄 reports/                           ← CLASSIFICATION DOCUMENTATION
    │   ├── 00_START_HERE.md                 (Classification quickstart)
    │   ├── 00_FEATURE_ENGINEERING_COMPLETE.md (FE completion status)
    │   ├── 00_ENHANCED_EXPERIMENT_COMPLETE.md (Enhanced experiment status)
    │   ├── CLASSIFICATION_RESULTS_REPORT.md (Detailed classification results)
    │   ├── COMPLETION_SUMMARY.txt           (Completion summary)
    │   ├── ENHANCED_DATASET_ANALYSIS.md     (Enhanced dataset analysis)
    │   ├── EXECUTIVE_SUMMARY.md             (High-level executive summary)
    │   ├── EXPERIMENT_ANSWERS.md            (Key findings & answers)
    │   ├── FEATURE_ENGINEERING_QUICKSTART.md (FE quickstart guide)
    │   ├── FEATURE_ENGINEERING_REPORT.md    (Detailed FE report)
    │   ├── PROJECT_STATUS.md                (Project status tracker)
    │   ├── README.md                        (Classification README)
    │   └── TRANSFORMATION_SUMMARY.md        (Transformation details)
    │
    └── 📈 results/                           ← CLASSIFICATION MODEL OUTPUTS
        ├── logistic_results.json            (Logistic baseline metrics)
        ├── logistic_results_enhanced.json   (Logistic enhanced metrics)
        ├── random_forest_results.json       (Random Forest baseline metrics)
        ├── random_forest_results_enhanced.json (Random Forest enhanced metrics)
        ├── xgboost_results.json             (XGBoost baseline metrics)
        ├── xgboost_results_enhanced.json    (XGBoost enhanced metrics)
        └── new_features.txt                 (List of new classification features)
```

---

## 🎯 QUICK NAVIGATION GUIDE

### I want to...

**Train a regression model:**
```
Go to: training/
Run: python train_linear.py (or train_rf.py, train_xgb.py)
```

**Train a classification model:**
```
Go to: classification_experiment/training/
Run: python train_logistic.py (or train_random_forest.py, train_xgboost.py)
```

**Preprocess raw data:**
```
Go to: utils/
Run: python preprocess_housing.py
```

**Apply feature engineering for classification:**
```
Go to: classification_experiment/experiments/
Run: python apply_feature_engineering.py
```

**Read analysis reports:**
```
Go to: reports/ (for regression)
Go to: classification_experiment/reports/ (for classification)
```

**Find datasets:**
```
Go to: data/
All CSV files are here
```

**Check model results:**
```
Go to: results/ (regression - will be empty until you run training)
Go to: classification_experiment/results/ (classification - has existing results)
```

---

## 📊 FILE COUNT SUMMARY

| Directory | Files | Type |
|-----------|-------|------|
| **Root** | 3 | Documentation |
| **data/** | 9 | CSV + Text |
| **training/** | 6 | Python Scripts |
| **experiments/** | 2 | Python Scripts |
| **reports/** | 12 | Markdown |
| **results/** | 0 | JSON (ready for use) |
| **utils/** | 1 | Python Script |
| **classification_experiment/training/** | 6 | Python Scripts |
| **classification_experiment/experiments/** | 6 | Python Scripts |
| **classification_experiment/reports/** | 13 | Markdown + Text |
| **classification_experiment/results/** | 7 | JSON + Text |
| **TOTAL** | **65** | |

---

## 🔍 FILE NAMING PATTERNS

### Python Scripts
- `train_*.py` → Model training scripts
- `*_enhanced.py` → Uses enhanced feature engineering
- `*_minimal_fe.py` → Uses minimal feature engineering
- `apply_*.py` → Data transformation scripts
- `compare_*.py` → Comparison utilities
- `check_*.py` / `validate_*.py` → Data validation
- `preprocess_*.py` → Data preprocessing

### Data Files
- `train.csv` / `test.csv` → Raw Kaggle data
- `cleaned_data.csv` → Post-cleaning
- `processed_data*.csv` → Fully processed, ready for training
- `*_fe.csv` → Includes feature engineering suffix

### Documentation
- `README.md` → Overview and quickstart
- `*_SUMMARY.md` → High-level summary reports
- `*_REPORT.md` → Detailed analysis reports
- `*_COMPLETE.md` → Completion status documents
- `00_*.md` → Entry point documents (read first)

### Results
- `*_results.json` → Model performance metrics
- `*_enhanced.json` → Results with enhanced features
- `*.txt` → Feature lists or summaries

---

## 🚦 PATH REFERENCE GUIDE

### From `training/*.py`:
- Data: `../data/processed_data.csv`
- Results: `../results/` (not currently used)

### From `experiments/*.py`:
- Data read: `../data/processed_data.csv`
- Data write: `../data/processed_data_minimal_fe.csv`

### From `utils/*.py`:
- Data read: `../data/train.csv`
- Data write: `../data/cleaned_data.csv`, `../data/processed_data.csv`

### From `classification_experiment/training/*.py`:
- Data: `../../data/processed_data.csv`
- Results: `../results/*.json`

### From `classification_experiment/experiments/*.py`:
- Data read: `../../data/processed_data.csv`
- Data write: `../../data/processed_data_classification_fe.csv`
- Reports: `../reports/*.md`
- Results: `../results/*.txt`

---

## 📌 IMPORTANT NOTES

1. **Always run scripts from their directory**
   - Scripts use relative paths
   - Example: `cd training && python train_linear.py`

2. **Data files are centralized**
   - All datasets in `data/` folder
   - Both regression and classification use same data source

3. **Results auto-save to correct locations**
   - Classification results → `classification_experiment/results/`
   - Regression results → `results/` (when implemented)

4. **Empty directories are intentional**
   - `results/` → Ready for future use
   - `classification_experiment/data/` → Uses parent `data/`
   - `classification_experiment/utils/` → Uses parent `utils/`

5. **Documentation is organized by domain**
   - Root `reports/` → Regression analysis
   - `classification_experiment/reports/` → Classification analysis

---

## 🎨 VISUAL LEGEND

```
📂 Directory (folder)
📄 Documentation file
📊 Data file / dataset
🚂 Training script
🧪 Experiment / utility script
📈 Results / outputs
🛠️ Utility / helper script
🎯 Major subdirectory
```

---

## 🔄 COMMON WORKFLOWS

### Complete Regression Workflow:
```
1. utils/ → preprocess_housing.py (generate processed_data.csv)
2. training/ → train_linear.py (baseline)
3. training/ → train_rf.py (comparison)
4. training/ → train_xgb.py (comparison)
5. reports/ → read FINAL_RESULTS_COMPARISON.md
```

### Complete Classification Workflow:
```
1. utils/ → preprocess_housing.py (if not done)
2. classification_experiment/experiments/ → apply_feature_engineering.py
3. classification_experiment/training/ → train_logistic.py
4. classification_experiment/training/ → train_random_forest.py
5. classification_experiment/training/ → train_xgboost.py
6. classification_experiment/reports/ → read EXECUTIVE_SUMMARY.md
```

### Feature Engineering Impact Study:
```
1. experiments/ → create_minimal_fe_dataset.py
2. training/ → train_*_minimal_fe.py (all 3 models)
3. experiments/ → compare_fe_impact.py
4. reports/ → read FE_IMPACT_ANALYSIS.md
```

---

**Last Updated:** June 13, 2026  
**Structure Version:** 1.0  
**Total Files:** 65  
**Total Directories:** 12
