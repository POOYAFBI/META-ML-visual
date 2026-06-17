# Deep Root Cause Report

## 1. Investigation Summary

This investigation traced the mismatch between training/report results and runtime/API results at file and artifact level. The scope covered:

- `save_all_models.py` model-persistence pipeline.
- `models/model_registry.json` registry metadata.
- Regression `.pkl` artifacts under `models/regression/**`.
- Classification `.pkl` artifacts under `models/classification/**`.
- Feature schema JSON files under `models/**/**/*_features.json`.
- Runtime backend loaders/evaluators under `backend/services/model_loader.py`, `backend/services/metrics.py`, and `backend/services/comparison.py`.
- Training scripts under `regression_experiment/training/` and `classification_experiment/training/`.
- Datasets under `data/`.
- Markdown reports under `regression_experiment/reports/`, `README.md`, and `models/README.md`.

The decisive deeper finding is that the feature JSON schemas are aligned with current runtime CSV column order, but the saved **regression Linear Regression `.pkl` artifacts themselves do not correspond to models freshly trained from the current datasets with the same split and feature schema**. The break is therefore at the **saved model artifact layer**, not at frontend rendering and not at runtime feature-order construction.

## 2. Confirmed Root Causes (MOST IMPORTANT)

### Root Cause 1 — Baseline Linear Regression artifact is not the model represented by reports/registry

- **Exact artifact:** `models/regression/baseline_dataset/linear_regression.pkl`
- **Linked feature schema:** `models/regression/baseline_dataset/linear_regression_features.json`
- **Linked runtime dataset:** `data/processed_data.csv`
- **Linked persistence script entry:** `save_all_models.py` maps regression `baseline_dataset` to `data/processed_data.csv` and `LinearRegression` with no scaling.
- **Exact issue:** The saved `.pkl` model coefficients/intercept do not match a fresh `LinearRegression` trained from the current `data/processed_data.csv` using the same feature order and `train_test_split(test_size=0.2, random_state=42)`.
- **Evidence:** Fresh current-dataset reproduction produced RMSE **$22,964.56**, R² **0.899518**. The saved artifact produced RMSE **$29,976.22**, R² **0.828791** on the same runtime test split. Coefficients were not equal, with maximum coefficient difference **24,804.72**, and intercepts differed by **45,117.96**.
- **Impact:** Runtime/API regression ranking is changed. The report/registry says baseline Linear Regression should be approximately best; runtime correctly evaluates the saved artifact and finds it much worse.

### Root Cause 2 — Enhanced/minimal Linear Regression artifact is not the model represented by reports/registry

- **Exact artifact:** `models/regression/enhanced_dataset/linear_regression.pkl`
- **Linked feature schema:** `models/regression/enhanced_dataset/linear_regression_features.json`
- **Linked runtime dataset:** `data/processed_data_minimal_fe.csv`
- **Linked persistence script entry:** `save_all_models.py` maps regression `enhanced_dataset` to `data/processed_data_minimal_fe.csv` and `LinearRegression` with no scaling.
- **Exact issue:** The saved `.pkl` model does not match a fresh model trained from the current minimal-FE dataset with the same split and feature order.
- **Evidence:** Fresh current-dataset reproduction produced RMSE **$23,223.15**, R² **0.897242**. The saved artifact produced RMSE **$33,534.72**, R² **0.785730** on the same runtime split. Coefficients were not equal, with maximum coefficient difference **19,922.50**, and intercepts differed by **108,382.40**.
- **Impact:** The runtime/API value for enhanced Linear Regression is catastrophically degraded relative to the reported minimal-FE result.

### Root Cause 3 — The registry and reports are not artifact-derived truth sources

- **Exact files:** `models/model_registry.json`, `regression_experiment/reports/XGB_TRAINING_SUMMARY.md`, `regression_experiment/reports/FE_IMPACT_ANALYSIS.md`, `models/README.md`, `README.md`.
- **Exact issue:** These files contain static training/report values that are not recomputed from the saved artifacts. Runtime metrics are recomputed by backend code from `.pkl` + feature JSON + CSV; registry/report values are separate stored claims.
- **Evidence:** Registry stores baseline Linear Regression R² **0.8996521449187238** and enhanced Linear Regression R² **0.8973549622374428**, while the saved artifacts produce R² **0.828791** and **0.785730** at runtime. Reports claim baseline Linear Regression RMSE **$22,974.15** and minimal-FE Linear Regression RMSE **$23,239.24**, close to fresh retraining but not to saved artifacts.
- **Impact:** Two truth sources exist: static documentation/registry versus runtime artifact evaluation. They diverge silently.

### Root Cause 4 — Feature schema is not the cause of the Linear Regression failure

- **Exact files:** all regression feature JSON files under `models/regression/baseline_dataset/` and `models/regression/enhanced_dataset/`.
- **Exact issue checked:** Feature count, feature names, and feature order were compared between current CSV columns and saved feature JSON files.
- **Evidence:** For all six regression models, feature JSON matched the current runtime dataset exactly: baseline models had **209/209** features with same order; enhanced/minimal models had **199/199** features with same order; no missing or extra features were found.
- **Impact:** The Linear Regression mismatch cannot be attributed to runtime feature order, missing features, extra features, or frontend/API schema construction. The broken component is the `.pkl` estimator payload itself.

### Root Cause 5 — Dataset naming creates traceability ambiguity, but not the primary metric break

- **Exact files:** `save_all_models.py`, `backend/services/model_loader.py`, `models/model_registry.json`.
- **Exact issue:** The label `enhanced_dataset` means different concrete files by task: regression enhanced means `data/processed_data_minimal_fe.csv`, classification enhanced means `data/processed_data_classification_fe.csv`.
- **Evidence:** The persistence script and backend loader both map regression enhanced to `processed_data_minimal_fe.csv`, while classification enhanced maps to `processed_data_classification_fe.csv`.
- **Impact:** This is a traceability hazard. It did not cause the Linear Regression metric collapse because the runtime and persistence mappings agree, but it makes forensic interpretation easier to misread.

## 3. Model Artifact Mapping

| Task | Dataset label | Concrete dataset | Training/persistence source | Feature schema file | Saved artifact | Runtime dataset used | Artifact/runtime verdict |
|---|---|---|---|---|---|---|---|
| Regression | baseline_dataset | `data/processed_data.csv` | `save_all_models.py` / `regression_experiment/training/train_linear.py` logic | `models/regression/baseline_dataset/linear_regression_features.json` | `models/regression/baseline_dataset/linear_regression.pkl` | `data/processed_data.csv` | **Wrong/stale artifact: does not match fresh training** |
| Regression | baseline_dataset | `data/processed_data.csv` | `save_all_models.py` / `train_rf.py` logic | `models/regression/baseline_dataset/random_forest_features.json` | `models/regression/baseline_dataset/random_forest.pkl` | `data/processed_data.csv` | Runtime close to registry/report; minor numeric drift |
| Regression | baseline_dataset | `data/processed_data.csv` | `save_all_models.py` / `train_xgb.py` logic | `models/regression/baseline_dataset/xgboost_features.json` | `models/regression/baseline_dataset/xgboost.pkl` | `data/processed_data.csv` | Runtime close to registry/report; minor numeric drift |
| Regression | enhanced_dataset | `data/processed_data_minimal_fe.csv` | `save_all_models.py` / `train_linear_minimal_fe.py` logic | `models/regression/enhanced_dataset/linear_regression_features.json` | `models/regression/enhanced_dataset/linear_regression.pkl` | `data/processed_data_minimal_fe.csv` | **Wrong/stale artifact: does not match fresh training** |
| Regression | enhanced_dataset | `data/processed_data_minimal_fe.csv` | `save_all_models.py` / `train_rf_minimal_fe.py` logic | `models/regression/enhanced_dataset/random_forest_features.json` | `models/regression/enhanced_dataset/random_forest.pkl` | `data/processed_data_minimal_fe.csv` | Runtime close to registry/report; minor numeric drift |
| Regression | enhanced_dataset | `data/processed_data_minimal_fe.csv` | `save_all_models.py` / `train_xgb_minimal_fe.py` logic | `models/regression/enhanced_dataset/xgboost_features.json` | `models/regression/enhanced_dataset/xgboost.pkl` | `data/processed_data_minimal_fe.csv` | Runtime close to registry/report; minor numeric drift |
| Classification | baseline_dataset | `data/processed_data.csv` | `save_all_models.py` / classification training scripts | `models/classification/baseline_dataset/logistic_regression_features.json` | `models/classification/baseline_dataset/logistic_regression.pkl` + scaler | `data/processed_data.csv` | Slight registry/runtime drift |
| Classification | baseline_dataset | `data/processed_data.csv` | `save_all_models.py` / classification training scripts | `models/classification/baseline_dataset/random_forest_features.json` | `models/classification/baseline_dataset/random_forest.pkl` | `data/processed_data.csv` | Slight registry/runtime drift |
| Classification | baseline_dataset | `data/processed_data.csv` | `save_all_models.py` / classification training scripts | `models/classification/baseline_dataset/xgboost_features.json` | `models/classification/baseline_dataset/xgboost.pkl` | `data/processed_data.csv` | Slight registry/runtime drift |
| Classification | enhanced_dataset | `data/processed_data_classification_fe.csv` | `save_all_models.py` / classification enhanced scripts | `models/classification/enhanced_dataset/logistic_regression_features.json` | `models/classification/enhanced_dataset/logistic_regression.pkl` + scaler | `data/processed_data_classification_fe.csv` | Slight registry/runtime drift |
| Classification | enhanced_dataset | `data/processed_data_classification_fe.csv` | `save_all_models.py` / classification enhanced scripts | `models/classification/enhanced_dataset/random_forest_features.json` | `models/classification/enhanced_dataset/random_forest.pkl` | `data/processed_data_classification_fe.csv` | Slight registry/runtime drift |
| Classification | enhanced_dataset | `data/processed_data_classification_fe.csv` | `save_all_models.py` / classification enhanced scripts | `models/classification/enhanced_dataset/xgboost_features.json` | `models/classification/enhanced_dataset/xgboost.pkl` | `data/processed_data_classification_fe.csv` | Slight registry/runtime drift |

## 4. Feature Schema Mismatch Analysis

Feature schema validation was performed by comparing each saved feature JSON list against the concrete CSV columns after excluding target columns `SalePrice` and `price_class`.

### Regression baseline schema

- Dataset: `data/processed_data.csv`
- CSV feature count: **209**
- Feature JSON files checked:
  - `models/regression/baseline_dataset/linear_regression_features.json`
  - `models/regression/baseline_dataset/random_forest_features.json`
  - `models/regression/baseline_dataset/xgboost_features.json`
- Result: **same count, same names, same order** for all three models.

### Regression enhanced/minimal schema

- Dataset: `data/processed_data_minimal_fe.csv`
- CSV feature count: **199**
- Feature JSON files checked:
  - `models/regression/enhanced_dataset/linear_regression_features.json`
  - `models/regression/enhanced_dataset/random_forest_features.json`
  - `models/regression/enhanced_dataset/xgboost_features.json`
- Result: **same count, same names, same order** for all three models.

### Linear Regression artifact internals

Both saved regression Linear Regression artifacts have `n_features_in_` matching the expected feature count, but no `feature_names_in_` because the persistence script trains unscaled models on `X_train.values`, not a pandas feature-named frame.

- Baseline artifact: `n_features_in_ = 209`, `feature_names_in_` absent.
- Enhanced/minimal artifact: `n_features_in_ = 199`, `feature_names_in_` absent.

This means the artifact cannot self-prove column names at inference. However, because external feature JSON order matches runtime CSV order, the observed failure is not caused by the current feature JSON files.

## 5. Dataset Version Analysis

### Dataset inventory and routing

| Dataset file | Used by | Feature count after target exclusion | Runtime route |
|---|---|---:|---|
| `data/processed_data.csv` | Regression baseline and classification baseline | 209 | `backend/services/model_loader.py` maps regression/classification baseline here |
| `data/processed_data_minimal_fe.csv` | Regression enhanced/minimal | 199 | `backend/services/model_loader.py` maps regression enhanced here |
| `data/processed_data_classification_fe.csv` | Classification enhanced | 212 | `backend/services/model_loader.py` maps classification enhanced here |

### Dataset drift findings

- Git history shows the relevant datasets, registry, and model artifacts all entered the repository in the same initial commit.
- Filesystem modification times are not reliable evidence of original training time because checkout materialized files at the current environment time.
- No alternate older dataset copy was found in the repository that can reproduce the saved Linear Regression artifacts.
- Fresh training on the current datasets reproduces the **report/registry Linear Regression performance**, not the saved `.pkl` Linear Regression performance.

### Dataset-level conclusion

The current datasets are not the immediate cause of the Linear Regression mismatch. The current datasets support the reported Linear Regression performance when retrained fresh. Therefore, the precise break is between the reported/current-data training logic and the committed saved `.pkl` Linear Regression artifacts.

## 6. Reproducibility Findings

### Reproduction method used

The reproducibility check used the same effective runtime/training logic:

1. Load current CSV.
2. Exclude `SalePrice` and `price_class` from features.
3. Convert booleans to numeric values consistently with runtime parsing.
4. Use `train_test_split(test_size=0.2, random_state=42)` for regression.
5. Train a fresh `LinearRegression` on current training rows.
6. Evaluate the fresh model and saved `.pkl` model on the same current test rows and same feature order.

### Regression Linear Regression reproducibility

| Artifact | Current fresh training result | Saved `.pkl` runtime result | Reproduces report? | Reproduces artifact? | Cause |
|---|---:|---:|---|---|---|
| `models/regression/baseline_dataset/linear_regression.pkl` | RMSE **$22,964.56**, R² **0.899518** | RMSE **$29,976.22**, R² **0.828791** | Fresh model: yes/near | Saved model: no | Saved estimator payload differs from expected training output |
| `models/regression/enhanced_dataset/linear_regression.pkl` | RMSE **$23,223.15**, R² **0.897242** | RMSE **$33,534.72**, R² **0.785730** | Fresh model: yes/near | Saved model: no | Saved estimator payload differs from expected training output |

### Other regression model reproducibility

| Artifact | Report/registry expectation | Runtime saved artifact | Finding |
|---|---:|---:|---|
| `models/regression/baseline_dataset/random_forest.pkl` | R² about **0.894238** | R² **0.893967**, RMSE **$23,590.38** | Minor numeric drift; not root break |
| `models/regression/baseline_dataset/xgboost.pkl` | R² about **0.898172** | R² **0.897557**, RMSE **$23,187.63** | Minor numeric drift; not root break |
| `models/regression/enhanced_dataset/random_forest.pkl` | R² about **0.886391** | R² **0.885816**, RMSE **$24,480.27** | Minor numeric drift; not root break |
| `models/regression/enhanced_dataset/xgboost.pkl` | R² about **0.887612** | R² **0.886278**, RMSE **$24,430.69** | Minor numeric drift; not root break |

### Classification reproducibility

Classification saved artifacts show small runtime-vs-registry differences, not the severe artifact failure seen in Linear Regression. Runtime metrics are recomputed with stratified split and optional scaler, consistent with the backend and logistic training pattern. The classification drift is lower severity and does not explain the major report/API contradiction.

## 7. Critical Findings (Top 3 Issues)

### 1. `models/regression/baseline_dataset/linear_regression.pkl` is the most damaging broken artifact

This artifact is the exact file that breaks the baseline regression truth chain. Reports and fresh current-data training support RMSE around **$22.96k–$22.97k**, but runtime evaluation of the committed `.pkl` returns **$29.98k**. That single artifact flips the baseline regression model ranking.

### 2. `models/regression/enhanced_dataset/linear_regression.pkl` is also broken

This artifact is even more degraded in absolute terms. Fresh current-data training supports RMSE around **$23.22k–$23.24k**, but the saved `.pkl` returns **$33.53k**. This proves the problem is not isolated to one dataset; both persisted regression Linear Regression estimators are inconsistent with the training/report lineage.

### 3. `models/model_registry.json` and Markdown reports are static claims, not verified artifact measurements

The registry and reports contain values that agree with fresh retraining, but they do not agree with committed Linear Regression artifacts. Runtime correctly evaluates artifacts, while documentation reports historical/training claims. The system breaks because it lacks a single artifact-derived truth source.

## 8. Final Root Cause Verdict

👉 **What exactly broke the system:**

The system broke at the **regression Linear Regression model artifact layer**.

The exact broken files are:

1. `models/regression/baseline_dataset/linear_regression.pkl`
2. `models/regression/enhanced_dataset/linear_regression.pkl`

These `.pkl` files do **not** correspond to the Linear Regression models produced by the current training logic, current datasets, current feature order, and report/registry metrics. The current datasets and feature JSON schemas are aligned; fresh Linear Regression training on those datasets reproduces the reported performance closely. Runtime/API evaluation is also behaving correctly by loading and scoring the committed artifacts.

Therefore, the truth diverges here:

`training/report/current-data LinearRegression result → saved .pkl artifact`

Not here:

- Not in frontend rendering.
- Not in `/api/comparison` computation.
- Not in current regression feature JSON order.
- Not in current runtime dataset routing.

Final file-level verdict:

**The committed Linear Regression regression `.pkl` artifacts are stale, overwritten from a different experiment, or otherwise not the estimator outputs for the reported/current-data training runs. Those two files are the precise root cause of the high-severity mismatch.**
