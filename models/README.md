# Saved Machine Learning Models

This directory contains **12 production-ready machine learning models** for house price prediction.

## 📁 Directory Structure

```
models/
├── README.md                          ← You are here
├── model_registry.json                ← Complete metadata for all 12 models
│
├── regression/                        ← 6 models for price prediction
│   ├── baseline_dataset/              ← 3 models (209 features)
│   │   ├── linear_regression.pkl
│   │   ├── random_forest.pkl
│   │   └── xgboost.pkl
│   └── enhanced_dataset/              ← 3 models (199 features, minimal FE)
│       ├── linear_regression.pkl
│       ├── random_forest.pkl
│       └── xgboost.pkl
│
└── classification/                    ← 6 models for category prediction
    ├── baseline_dataset/              ← 3 models (209 features)
    │   ├── logistic_regression.pkl    ⚠️ Requires scaler!
    │   ├── random_forest.pkl
    │   └── xgboost.pkl
    └── enhanced_dataset/              ← 3 models (212 features, with FE)
        ├── logistic_regression.pkl    ⚠️ Requires scaler!
        ├── random_forest.pkl
        └── xgboost.pkl
```

## 🎯 Model Types

### Regression Models
**Task:** Predict exact house sale price (continuous value)  
**Output:** Dollar amount (e.g., $185,000)  
**Best Model:** Linear Regression (Baseline) - R² = 0.8997

### Classification Models
**Task:** Predict price category (Low / Medium / High)  
**Output:** Class label (0, 1, or 2)  
**Best Model:** Random Forest (Baseline) - Accuracy = 84.59%

## ⚡ Quick Usage

```python
import joblib

# Regression
model = joblib.load('models/regression/baseline_dataset/xgboost.pkl')
price = model.predict(X_new)

# Classification
model = joblib.load('models/classification/baseline_dataset/random_forest.pkl')
category = model.predict(X_new)  # 0=Low, 1=Medium, 2=High
```

## ⚠️ Important Notes

1. **Logistic Regression requires scaling:**
   ```python
   model = joblib.load('models/classification/.../logistic_regression.pkl')
   scaler = joblib.load('models/classification/.../logistic_regression_scaler.pkl')
   X_scaled = scaler.transform(X_new)
   predictions = model.predict(X_scaled)
   ```

2. **Feature order matters:** Use the `*_features.json` files to validate input

3. **All models use the same train/test split:** `random_state=42`

## 📊 Model Performance

See `model_registry.json` for complete performance metrics.

## 📖 Documentation

- **Detailed Report:** `../MODEL_PERSISTENCE_REPORT.md`
- **Quick Start:** `../QUICK_START_GUIDE.md`
- **Test Script:** `../test_model_loading.py`

## 🔄 Retraining

To retrain all models:
```bash
python save_all_models.py
```

---

**Last Updated:** 2026-06-13  
**Models Saved:** 12 / 12  
**Status:** ✅ Production Ready
