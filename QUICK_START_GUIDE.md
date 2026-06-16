# QUICK START GUIDE: Using Saved Models

## 🚀 Load and Use a Model in 30 Seconds

### Example 1: Regression (Predict House Price)

```python
import joblib
import pandas as pd

# Load the model
model = joblib.load('models/regression/baseline_dataset/xgboost.pkl')

# Prepare your data (must have 209 features in correct order)
# X_new should be a pandas DataFrame or numpy array
predictions = model.predict(X_new)

print(f"Predicted house price: ${predictions[0]:,.2f}")
```

### Example 2: Classification (Predict Price Category)

```python
import joblib
import pandas as pd

# Load the model
model = joblib.load('models/classification/baseline_dataset/random_forest.pkl')

# Prepare your data
predictions = model.predict(X_new)

# 0 = Low, 1 = Medium, 2 = High
category_names = ['Low', 'Medium', 'High']
print(f"Predicted category: {category_names[predictions[0]]}")
```

### Example 3: Logistic Regression (REQUIRES SCALING!)

```python
import joblib
import pandas as pd

# Load BOTH model and scaler
model = joblib.load('models/classification/baseline_dataset/logistic_regression.pkl')
scaler = joblib.load('models/classification/baseline_dataset/logistic_regression_scaler.pkl')

# MUST scale features before prediction
X_scaled = scaler.transform(X_new)
predictions = model.predict(X_scaled)

print(f"Predicted category: {predictions[0]}")
```

---

## 📋 Model Selection Guide

### For Regression (Predicting Exact House Price)

| Use Case | Recommended Model | File Path |
|----------|------------------|-----------|
| Best overall accuracy | Linear Regression (Baseline) | `models/regression/baseline_dataset/linear_regression.pkl` |
| Fast inference | Linear Regression | `models/regression/baseline_dataset/linear_regression.pkl` |
| Capturing non-linear patterns | XGBoost or Random Forest | `models/regression/baseline_dataset/xgboost.pkl` |
| Fewer features (199 vs 209) | Enhanced dataset models | `models/regression/enhanced_dataset/*` |

### For Classification (Predicting Price Category: Low/Medium/High)

| Use Case | Recommended Model | File Path |
|----------|------------------|-----------|
| Best overall accuracy | Random Forest (Baseline) | `models/classification/baseline_dataset/random_forest.pkl` |
| Fastest inference | Logistic Regression | `models/classification/baseline_dataset/logistic_regression.pkl` |
| Balanced performance | XGBoost | `models/classification/baseline_dataset/xgboost.pkl` |
| With feature engineering | Enhanced dataset models | `models/classification/enhanced_dataset/*` |

---

## 🔍 Feature Validation

Always validate your input features match the model's expected features:

```python
import json

# Load expected feature names
with open('models/regression/baseline_dataset/linear_regression_features.json', 'r') as f:
    feature_info = json.load(f)
    expected_features = feature_info['feature_names']

# Validate input DataFrame
if list(X_new.columns) != expected_features:
    # Reorder to match
    X_new = X_new[expected_features]
```

---

## ⚙️ Model Performance Reference

### Regression Models (Test R² Score)
| Model | Baseline (209 features) | Enhanced (199 features) |
|-------|------------------------|-------------------------|
| Linear Regression | **0.8997** ⭐ | 0.8974 |
| Random Forest | 0.8942 | 0.8864 |
| XGBoost | 0.8982 | 0.8876 |

### Classification Models (Test Accuracy)
| Model | Baseline (209 features) | Enhanced (212 features) |
|-------|------------------------|-------------------------|
| Logistic Regression | 0.7979 | 0.8219 |
| Random Forest | **0.8459** ⭐ | 0.8253 |
| XGBoost | 0.8425 | 0.8185 |

⭐ = Best performing model in category

---

## 🐛 Common Errors and Solutions

### Error: "Feature shape mismatch"
**Problem:** Input has wrong number of features  
**Solution:** Check expected features in `*_features.json` file

```python
# Check expected feature count
with open('models/.../model_features.json') as f:
    num_features = len(json.load(f)['feature_names'])
print(f"Expected features: {num_features}")
print(f"Your data features: {X_new.shape[1]}")
```

### Error: "Model predictions are nonsensical"
**Problem:** Forgot to scale features for logistic regression  
**Solution:** Load and apply the scaler before prediction

```python
# Always check if a scaler file exists
scaler_path = 'models/.../logistic_regression_scaler.pkl'
if Path(scaler_path).exists():
    scaler = joblib.load(scaler_path)
    X_new = scaler.transform(X_new)
```

### Error: "FileNotFoundError"
**Problem:** Running from wrong directory  
**Solution:** Use absolute paths or change to project root

```python
from pathlib import Path

# Set base directory
BASE_DIR = Path(__file__).parent
model_path = BASE_DIR / 'models' / 'regression' / 'baseline_dataset' / 'xgboost.pkl'
model = joblib.load(model_path)
```

---

## 📦 Required Dependencies

```bash
pip install scikit-learn xgboost pandas numpy joblib
```

Specific versions used in training:
- scikit-learn: 1.3+
- xgboost: 2.0+
- pandas: 2.0+
- numpy: 1.24+

---

## 🧪 Test Your Setup

Run the provided test script:

```bash
python test_model_loading.py
```

Expected output: `✅ ALL MODELS PASSED LOADING TEST`

---

## 📚 Additional Resources

- **Full Report:** `MODEL_PERSISTENCE_REPORT.md`
- **Model Registry:** `models/model_registry.json`
- **Training Script:** `save_all_models.py`
- **Test Script:** `test_model_loading.py`

---

## 💡 Production Tips

1. **Cache loaded models** in memory instead of loading on every request
2. **Add input validation** to check for missing values, outliers, feature types
3. **Log predictions** for monitoring and debugging
4. **Version your models** (e.g., add v1.0, v2.0 subdirectories)
5. **Set up model A/B testing** to compare different models in production
6. **Monitor model performance** and retrain when accuracy degrades

---

**Quick Start Guide v1.0**  
Last Updated: 2026-06-13
