# Truth Audit Report

## 1. Executive Summary

This audit inspected the repository end-to-end across training scripts, saved model artifacts, dataset mappings, backend evaluation code, frontend rendering code, model registry metadata, and Markdown reports.

**Final high-level conclusion: the system is partially inconsistent and can be misleading.** The saved model files are loadable and the backend/UI comparison tables are not hardcoded; however, the runtime metrics produced from the saved `.pkl` files do **not** match several reported training/report metrics, and the current runtime ranking contradicts the project reports for regression. The largest verified issue is that the saved regression linear models behave as if they are stale or not the same models/feature schema used for the reported training results.

Key findings:

- Runtime comparison values are computed from saved models and datasets through backend code, not static frontend constants.
- Reported regression results claim **Linear Regression baseline** is best, but saved-model runtime evaluation ranks **XGBoost baseline** best.
- Runtime RMSE for saved baseline Linear Regression is **$29,976.22**, while reports claim about **$22,974.15**.
- Runtime RMSE for saved enhanced/minimal Linear Regression is **$33,534.72**, while reports claim **$23,239.24**.
- Random Forest and XGBoost saved regression artifacts are close to registry/report R² values but still not identical to several Markdown report RMSE values.
- Classification runtime metrics are close to registry metadata but not exactly equal; backend uses stratified evaluation, matching training scripts, while registry values appear slightly different.
- The UI comparison section uses `/api/comparison` live API data, but the displayed values inherit backend/model inconsistencies.

## 2. Verified Truth

The following items were verified as correct and consistent with code or artifacts:

1. **The backend loads real `.pkl` model files and feature JSON files from the registry.** The loader reads `models/model_registry.json`, resolves model paths, loads feature names, loads `.pkl` models with `joblib`, and maps each model to a runtime data path.
   - Evidence: `load_bundle()` reads registry model metadata, feature JSON, model `.pkl`, optional scaler `.pkl`, and data path.
   - Source: `backend/services/model_loader.py` lines 91-129.

2. **Runtime regression and classification metrics are computed from saved models, not manually embedded in the frontend.** Runtime evaluation reloads the model bundle, rebuilds `X`/`y` from CSV data, uses `train_test_split(test_size=0.2, random_state=42)`, predicts with the saved model, and computes RMSE/R² or Accuracy/F1.
   - Evidence: `evaluation()` in `backend/services/metrics.py` lines 63-82.

3. **The comparison API derives table rows from runtime evaluation, not registry `test_score` alone.** The comparison code calls `evaluation()` for each registry model, then computes RMSE, MAE, R², Accuracy, Weighted F1, and Macro F1 for rows.
   - Evidence: `backend/services/comparison.py` lines 57-102.

4. **The frontend comparison UI requests live backend data from `/api/comparison`.** It validates and renders the API response into the comparison table/charts.
   - Evidence: `frontend/app.js` lines 648-669.

5. **Dataset routing is explicit and internally coherent in the backend.** Runtime maps regression baseline to `data/processed_data.csv`, regression enhanced to `data/processed_data_minimal_fe.csv`, classification baseline to `data/processed_data.csv`, and classification enhanced to `data/processed_data_classification_fe.csv`.
   - Evidence: `backend/services/model_loader.py` lines 33-38.

6. **Training scripts use the expected core split pattern.** Regression baseline training uses `data/processed_data.csv`, excludes `SalePrice` and `price_class`, fills missing values with feature means if present, and uses `train_test_split(..., test_size=0.2, random_state=42)`.
   - Evidence: `regression_experiment/training/train_linear.py` lines 20-65.

7. **Classification training uses stratified split and scaling where appropriate for logistic regression.** Logistic training uses `train_test_split(..., stratify=y)` and `StandardScaler`.
   - Evidence: `classification_experiment/training/train_logistic.py` lines 59-72.

## 3. Inconsistencies Found

### 3.1 Regression report claims do not match saved-model runtime truth

Reports state the baseline regression ranking is:

1. Linear Regression — RMSE **$22,974.15**
2. XGBoost — RMSE **$23,072.61**
3. Random Forest — RMSE **$23,133.58**

Evidence: `regression_experiment/reports/XGB_TRAINING_SUMMARY.md` lines 24-30.

Runtime saved-model evaluation produced:

1. baseline XGBoost — RMSE **$23,187.63**, R² **0.897557**
2. baseline Random Forest — RMSE **$23,590.38**, R² **0.893967**
3. enhanced XGBoost — RMSE **$24,430.69**, R² **0.886278**
4. enhanced Random Forest — RMSE **$24,480.27**, R² **0.885816**
5. baseline Linear Regression — RMSE **$29,976.22**, R² **0.828791**
6. enhanced Linear Regression — RMSE **$33,534.72**, R² **0.785730**

This is a material contradiction. The report says Linear Regression baseline is best; saved-model runtime says Linear Regression baseline is fifth out of six regression rows.

### 3.2 Model registry says Linear Regression has strong R², but saved model runtime does not

The registry records baseline Linear Regression `test_score` as **0.8996521449187238** and enhanced Linear Regression `test_score` as **0.8973549622374428**.

Evidence: `models/model_registry.json` lines 8-21 and 53-66.

Runtime saved-model evaluation found:

- baseline Linear Regression R² **0.828791**
- enhanced Linear Regression R² **0.785730**

This strongly suggests the saved Linear Regression `.pkl` artifacts are stale, mismatched, or incompatible with the exact feature/data ordering used at runtime.

### 3.3 FE impact report does not match saved-model runtime behavior

The FE impact report states:

- Linear Regression Full FE RMSE **$22,974.15**, Minimal FE RMSE **$23,239.24**
- Random Forest Full FE RMSE **$23,133.58**, Minimal FE RMSE **$24,218.50**
- XGBoost Full FE RMSE **$23,072.84**, Minimal FE RMSE **$24,618.88**

Evidence: `regression_experiment/reports/FE_IMPACT_ANALYSIS.md` lines 52-59.

Runtime saved-model evaluation found:

- Linear Regression baseline RMSE **$29,976.22**, enhanced/minimal RMSE **$33,534.72**
- Random Forest baseline RMSE **$23,590.38**, enhanced/minimal RMSE **$24,480.27**
- XGBoost baseline RMSE **$23,187.63**, enhanced/minimal RMSE **$24,430.69**

The linear model mismatch is severe; Random Forest and XGBoost are directionally similar but numerically inconsistent.

### 3.4 README and models README contain stale or incomplete performance summaries

`README.md` lists only partial regression values and uses `TBD` for several entries; it also reports XGBoost as approximately `$23,000` instead of a concrete saved-model runtime value.

Evidence: `README.md` lines 99-111.

`models/README.md` claims:

- Best Regression Model: Linear Regression baseline, R² **0.8997**
- Best Classification Model: Random Forest baseline, Accuracy **84.59%**

Evidence: `models/README.md` lines 35-43.

Runtime saved-model comparison instead ranks:

- Regression: baseline XGBoost best by RMSE.
- Classification: baseline XGBoost best by Weighted F1, with baseline Random Forest tied on Accuracy but slightly lower Weighted F1.

### 3.5 Registry metrics and runtime API metrics are not the same source of truth

The model registry stores `test_score` values, but the API does not return those values directly. The API recomputes metrics from saved models and CSVs.

Evidence:

- Registry contains static `test_score` fields: `models/model_registry.json` lines 16-17, 31-32, 46-47, 61-62, 76-77, and 91-92.
- Runtime evaluation recomputes metrics from saved model predictions: `backend/services/metrics.py` lines 63-82.
- Comparison rows use evaluation output, not registry `test_score`: `backend/services/comparison.py` lines 74-100.

This means reports/registry and API can diverge silently.

### 3.6 Dataset label “enhanced_dataset” is overloaded

The registry and UI label regression `enhanced_dataset`, but backend routing maps regression enhanced to `processed_data_minimal_fe.csv`, while classification enhanced maps to `processed_data_classification_fe.csv`.

Evidence: `backend/services/model_loader.py` lines 33-38 and 40-48.

This is technically implemented, but auditor verdict is **naming risk**: users may think “enhanced_dataset” means one common enhanced dataset, while regression and classification use different enhanced CSVs.

## 4. Model Consistency Analysis

### Regression models

| Model | Dataset used at runtime | Feature set | Training/report RMSE | Report RMSE | API/runtime RMSE | Consistency verdict |
|---|---:|---:|---:|---:|---:|---|
| Linear Regression | `data/processed_data.csv` | 209 | $22,974.15 reported | $22,974.15 | **$29,976.22** | **Inconsistent / high-risk stale artifact suspected** |
| Random Forest | `data/processed_data.csv` | 209 | $23,133.58 reported | $23,133.58 | **$23,590.38** | Inconsistent numerically, but directionally close |
| XGBoost | `data/processed_data.csv` | 209 | $23,072.61 / $23,072.84 reported | ~$23,073 | **$23,187.63** | Slightly inconsistent |
| Linear Regression | `data/processed_data_minimal_fe.csv` | 199 | $23,239.24 reported | $23,239.24 | **$33,534.72** | **Severely inconsistent / high-risk stale artifact suspected** |
| Random Forest | `data/processed_data_minimal_fe.csv` | 199 | $24,218.50 reported | $24,218.50 | **$24,480.27** | Slightly inconsistent |
| XGBoost | `data/processed_data_minimal_fe.csv` | 199 | $24,618.88 reported | $24,618.88 | **$24,430.69** | Slightly inconsistent |

### Classification models

| Model | Dataset used at runtime | Feature set | Registry/report metric | API/runtime metric | Consistency verdict |
|---|---:|---:|---:|---:|---|
| Logistic Regression | `data/processed_data.csv` | 209 | Registry accuracy 0.797945 | Runtime accuracy **0.784247**, weighted F1 **0.783311** | Slightly inconsistent |
| Random Forest | `data/processed_data.csv` | 209 | Registry accuracy 0.845890 | Runtime accuracy **0.839041**, weighted F1 **0.839293** | Slightly inconsistent |
| XGBoost | `data/processed_data.csv` | 209 | Registry accuracy 0.842466 | Runtime accuracy **0.839041**, weighted F1 **0.840096** | Slightly inconsistent; runtime best by weighted F1 |
| Logistic Regression | `data/processed_data_classification_fe.csv` | 212 | Registry accuracy 0.821918 | Runtime accuracy **0.815068**, weighted F1 **0.816440** | Slightly inconsistent |
| Random Forest | `data/processed_data_classification_fe.csv` | 212 | Registry accuracy 0.825342 | Runtime accuracy **0.818493**, weighted F1 **0.818187** | Slightly inconsistent |
| XGBoost | `data/processed_data_classification_fe.csv` | 212 | Registry accuracy 0.818493 | Runtime accuracy **0.815068**, weighted F1 **0.813900** | Slightly inconsistent |

## 5. Pipeline Trace Analysis

### 5.1 Training pipeline observed

Regression training scripts generally follow:

`CSV dataset → drop SalePrice/price_class → fill missing numeric values if present → train_test_split(test_size=0.2, random_state=42) → fit model → compute RMSE/R²`

Evidence: `regression_experiment/training/train_linear.py` lines 20-65.

Classification logistic pipeline follows:

`CSV dataset → train_test_split(test_size=0.2, random_state=42, stratify=y) → StandardScaler → fit model → evaluate`

Evidence: `classification_experiment/training/train_logistic.py` lines 59-72.

### 5.2 Runtime inference/evaluation pipeline observed

Runtime comparison/evaluation follows:

`registry → model path + feature JSON → backend dataset mapping → CSV row parsing → train_test_split → optional scaler → saved .pkl predict → metric computation → API response → UI rendering`

Evidence:

- Model/feature/dataset loading: `backend/services/model_loader.py` lines 115-129.
- CSV to `X`/`y`: `backend/services/metrics.py` lines 52-60.
- Evaluation split and metrics: `backend/services/metrics.py` lines 63-82.
- API comparison row generation: `backend/services/comparison.py` lines 57-102.
- Frontend API consumption/rendering: `frontend/app.js` lines 648-669.

### 5.3 Mismatch locations

1. **Saved model artifact vs registry/report metrics**
   - Most severe for Linear Regression regression artifacts.
   - Registry says R² ≈ 0.90; saved model runtime says R² ≈ 0.83 and 0.79.

2. **Markdown reports vs runtime saved artifacts**
   - Reports rank Linear Regression best for baseline regression.
   - Runtime ranks XGBoost best.

3. **Registry `test_score` vs API metric source**
   - Registry stores static values, but API recomputes live from saved models and datasets.
   - These two sources are not synchronized.

4. **Dataset naming vs actual data file**
   - `enhanced_dataset` points to different CSVs depending on task; regression enhanced means minimal FE, classification enhanced means classification-specific FE.

## 6. UI vs Backend Truth Check

### Real values

The comparison UI uses live API data from `/api/comparison`, not hardcoded model metrics. The frontend calls the endpoint and renders returned rows directly.

Evidence: `frontend/app.js` lines 648-669.

### Suspicious or misleading values

1. **UI comparison values are real backend values but may conflict with reports.**
   - The UI truth source is runtime backend evaluation.
   - The report truth source is Markdown/registry values.
   - These sources disagree.

2. **README/model documentation values are stale/incomplete.**
   - `README.md` includes `TBD` and approximate values.
   - `models/README.md` declares Linear Regression best for regression, contradicting runtime.

Evidence: `README.md` lines 99-111 and `models/README.md` lines 35-43.

3. **No evidence was found that the UI comparison table uses fake static metric constants.**
   - Verdict: UI is not fake, but it displays metrics from a backend pipeline that is inconsistent with documentation and saved registry metadata.

## 7. Root Cause Analysis

### Issue 1 — Saved Linear Regression regression artifacts do not match reported training performance

- **Description:** Saved baseline/enhanced Linear Regression `.pkl` files produce much worse runtime RMSE/R² than registry and Markdown reports.
- **Evidence:** Registry reports baseline Linear Regression R² 0.899652 and enhanced R² 0.897355, while runtime produced R² 0.828791 and 0.785730. Registry evidence is in `models/model_registry.json` lines 8-21 and 53-66.
- **Root cause:** UNKNOWN with high suspicion of stale `.pkl` files, wrong feature ordering/schema at save time, or model artifacts saved from a different preprocessing/data state than the reports.
- **Risk level:** High.

### Issue 2 — Reported “best regression model” is contradicted by runtime API behavior

- **Description:** Reports say baseline Linear Regression is best; runtime says baseline XGBoost is best.
- **Evidence:** Report ranking is in `regression_experiment/reports/XGB_TRAINING_SUMMARY.md` lines 24-30. Runtime comparison computes ranking from runtime RMSE in `backend/services/comparison.py` lines 57-64 and 85-93.
- **Root cause:** Reports and saved artifacts are not synchronized. The report likely reflects script output from a different model artifact state than current saved `.pkl` files.
- **Risk level:** High.

### Issue 3 — FE impact report is not reproducible from current saved models

- **Description:** Minimal/full FE RMSE values in FE report differ from current saved-model runtime evaluation.
- **Evidence:** FE report table is in `regression_experiment/reports/FE_IMPACT_ANALYSIS.md` lines 52-59. Runtime evaluation recomputes metrics from saved `.pkl` files in `backend/services/metrics.py` lines 63-82.
- **Root cause:** UNKNOWN; likely artifact/report drift.
- **Risk level:** High for Linear Regression, Medium for tree models.

### Issue 4 — Registry static scores are not the API source of truth

- **Description:** Registry contains static `test_score`, but API recomputes metrics dynamically, producing different values.
- **Evidence:** Static registry values are in `models/model_registry.json` lines 16-17, 31-32, 46-47, 61-62, 76-77, and 91-92. Runtime API metrics are computed in `backend/services/metrics.py` lines 63-82.
- **Root cause:** Dual truth sources without validation/synchronization.
- **Risk level:** Medium.

### Issue 5 — Dataset naming can mislead reviewers/users

- **Description:** `enhanced_dataset` is used for regression minimal FE and classification-specific FE, which are different CSVs.
- **Evidence:** Dataset mapping is in `backend/services/model_loader.py` lines 33-38; display labels are in lines 40-48.
- **Root cause:** Overloaded registry dataset name.
- **Risk level:** Medium.

### Issue 6 — Documentation is stale/incomplete

- **Description:** README contains approximate and TBD metrics; models README contains best-model claims contradicted by runtime.
- **Evidence:** `README.md` lines 99-111 and `models/README.md` lines 35-43.
- **Root cause:** Documentation was not updated after model persistence/runtime comparison behavior changed.
- **Risk level:** Medium.

## 8. Final Verdict (VERY IMPORTANT)

👉 **The system is partially inconsistent and potentially misleading.**

It is **not fully reliable** because current saved-model runtime results, registry scores, and Markdown reports do not agree. It is also **not entirely fake**: the UI comparison path uses live backend API data, and the backend computes metrics from saved `.pkl` models and CSV datasets.

The decisive truth is:

- **Runtime/API truth:** baseline XGBoost is currently the best regression model by recomputed saved-model RMSE, and baseline XGBoost is currently the best classification model by weighted F1.
- **Report/documentation truth:** reports claim baseline Linear Regression is the best regression model and report substantially better Linear Regression RMSE/R².
- **Artifact truth:** saved Linear Regression regression artifacts do not reproduce their reported results and are the strongest evidence of stale or mismatched model persistence.

Final classification of the project state: **Partially inconsistent, with high-risk misleading regression documentation and likely stale/mismatched Linear Regression artifacts.**
