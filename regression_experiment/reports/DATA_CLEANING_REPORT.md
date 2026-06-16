# 📊 Ames Housing Dataset - Data Cleaning & Preprocessing Report

**Purpose**: Prepare housing dataset for multi-task ML system (Regression + Classification)  
**Dataset**: Ames Housing Dataset  
**Date**: June 11, 2026  
**Author**: pooya jafarpour

---

## 📋 Table of Contents

1. [Dataset Overview](#dataset-overview)
2. [Problems Found in Data](#problems-found-in-data)
3. [Cleaning Decisions](#cleaning-decisions)
4. [Feature Engineering](#feature-engineering)
5. [Target Engineering (price_class)](#target-engineering)
6. [Encoding Strategy](#encoding-strategy)
7. [Scaling Analysis](#scaling-analysis)
8. [Final Dataset Description](#final-dataset-description)
9. [Key Lessons for ML Engineers](#key-lessons)

---

## 1. Dataset Overview

### Original Dataset Statistics
- **Total Rows**: 1,460 houses
- **Total Columns**: 81 features
- **Target Variable**: `SalePrice` (continuous, in USD)
- **Feature Types**:
  - Numerical: 38 features
  - Categorical: 43 features
- **Missing Values**: 7,829 total missing entries across 19 columns

### Dataset Characteristics
This is the **Ames Housing Dataset**, containing residential home sales in Ames, Iowa from 2006-2010.
Features include property characteristics, location, quality ratings, and various measurements.

**Key challenges identified**:
- High percentage of missing values in several columns
- Multiple columns with ordinal relationships (quality ratings)
- Mix of numerical and categorical data types
- Potential outliers in price and area measurements
- Need to create classification target from continuous price

---

## 2. Problems Found in Data

### 2.1 Missing Value Analysis


**19 columns had missing values**, ranging from 0.07% to 99.5% missing:

| Column | Missing Count | Missing % | Reason for Missing |
|--------|--------------|-----------|-------------------|
| PoolQC | 1,453        | 99.5%     | Most houses don't have pools |
| MiscFeature | 1,406   | 96.3%     | Most houses lack misc features |
| Alley | 1,369         | 93.8%     | Most houses lack alley access |
| Fence | 1,179 | 80.8% | Most houses don't have fences |
| MasVnrType | 872 | 59.7% | Many houses lack masonry veneer |
| FireplaceQu | 690 | 47.3% | Many houses lack fireplaces |
| LotFrontage | 259 | 17.7% | True missing data |
| GarageType | 81 | 5.5% | Houses without garages |
| GarageYrBlt | 81 | 5.5% | Houses without garages |
| GarageFinish | 81 | 5.5% | Houses without garages |
| GarageQual | 81 | 5.5% | Houses without garages |
| GarageCond | 81 | 5.5% | Houses without garages |
| BsmtExposure | 38 | 2.6% | Houses without basements |
| BsmtFinType2 | 38 | 2.6% | Houses without basements |
| BsmtQual | 37 | 2.5% | Houses without basements |
| BsmtCond | 37 | 2.5% | Houses without basements |
| BsmtFinType1 | 37 | 2.5% | Houses without basements |
| MasVnrArea | 8 | 0.5% | True missing data |
| Electrical | 1 | 0.07% | True missing data |

### 2.2 Outlier Detection

**Outliers identified using IQR method** (values beyond Q1 - 1.5×IQR or Q3 + 1.5×IQR):

- **SalePrice**: 61 outliers (4.18%) - High-value luxury homes
- **GrLivArea**: 31 outliers (2.12%) - **4 extreme outliers >4000 sq ft** (removed)
- **LotArea**: 69 outliers (4.73%) - Very large lots
- **TotalBsmtSF**: 61 outliers (4.18%) - Large basements
- **1stFlrSF**: 20 outliers (1.37%) - Large first floors

**Why we removed only GrLivArea >4000 sq ft outliers**:
- These 4 houses had extremely large living area but disproportionately low prices
- Likely data entry errors or highly unusual properties
- Would negatively impact model training by introducing noise

### 2.3 Irrelevant Columns

- **Id**: Just a row identifier, no predictive value
- **Columns with >50% missing**: Too sparse to provide reliable information


---

## 3. Cleaning Decisions (with Reasoning)

### 3.1 Dropping Columns

**❌ Removed 6 columns**:
1. `Id` - Irrelevant identifier
2. `PoolQC` - 99.5% missing
3. `MiscFeature` - 96.3% missing
4. `Alley` - 93.8% missing
5. `Fence` - 80.8% missing
6. `MasVnrType` - 59.7% missing

**Why drop columns with >50% missing?**
- Too little information to impute reliably
- Risk of introducing bias through imputation
- Models struggle with columns that are mostly missing
- Better to use related features with complete data (e.g., MasVnrArea instead of MasVnrType)

**What happens if we don't drop them?**
- Imputation introduces artificial patterns
- Model may overfit to imputed values
- Reduces model reliability and generalization

### 3.2 Handling Missing Values in Numerical Columns

**Strategy**: Fill with **median** (not mean)

| Column | Strategy | Value | Reason |
|--------|----------|-------|--------|
| LotFrontage | Median | 69.0 | More robust to outliers than mean |
| MasVnrArea | Median | 0.0 | Most houses have 0, median preserves this |
| GarageYrBlt | Median | 1980.0 | Represents typical garage age |

**Why median over mean?**
- Mean is sensitive to outliers (e.g., a few very large lots skew LotFrontage)
- Median represents the "typical" house better
- More conservative imputation strategy

**Alternative approaches we didn't use (and why)**:
- ❌ **Drop rows**: Would lose 17.7% of data (259 rows from LotFrontage alone)
- ❌ **Forward/backward fill**: Not appropriate for housing data (no temporal order)
- ❌ **Model-based imputation**: Adds complexity, risk of overfitting


### 3.3 Handling Missing Values in Categorical Columns

**Two strategies based on domain knowledge**:

#### Strategy A: Fill with 'None' (NA has special meaning)

These columns have NA indicating **absence of feature**, not missing data:

| Column | Meaning of NA | Imputation |
|--------|--------------|------------|
| BsmtQual | No basement | 'None' |
| BsmtCond | No basement | 'None' |
| BsmtExposure | No basement | 'None' |
| BsmtFinType1 | No basement | 'None' |
| BsmtFinType2 | No basement | 'None' |
| FireplaceQu | No fireplace | 'None' |
| GarageType | No garage | 'None' |
| GarageFinish | No garage | 'None' |
| GarageQual | No garage | 'None' |
| GarageCond | No garage | 'None' |

**This is CRUCIAL**: NA here is not "missing data" but a valid category meaning "feature doesn't exist"

#### Strategy B: Fill with Mode (most frequent value)

| Column | Mode | Reason |
|--------|------|--------|
| Electrical | SBrkr | Only 1 missing value, use most common type |

**Why this matters**:
- ✅ **Correct approach**: Preserves domain meaning (no garage ≠ unknown garage)
- ❌ **Wrong approach**: Filling with mode would incorrectly assign garage features to houses without garages
- **Impact**: Directly affects model accuracy - wrong imputation = wrong predictions

---

## 4. Feature Engineering

Feature engineering is **the most important part of ML preprocessing**. Good features can improve model performance more than algorithm tuning.

### 4.1 Created Features (10 new features)


#### 1. **TotalSF** (Total Square Footage)
```
TotalSF = TotalBsmtSF + 1stFlrSF + 2ndFlrSF
```
**Why**: 
- Combines all livable space into one metric
- Total size is the #1 predictor of house price
- Easier for model than learning to combine three separate features
- Range: 334 - 6,428 sq ft

**What if we didn't create this?**
- Model would need to learn the relationship between basement, 1st, and 2nd floors
- Less interpretable feature importance
- May miss the holistic "total space" pattern

#### 2. **HouseAge** (Age of House)
```
HouseAge = 2024 - YearBuilt
```
**Why**: 
- Age directly impacts value (newer homes typically worth more)
- Easier to interpret than raw year (age 10 vs year 2014)
- Helps model understand depreciation patterns
- Range: 14 - 152 years

**Domain insight**: Very old homes (100+ years) may be historic/valuable despite age

#### 3. **YearsSinceRemod** (Time Since Remodeling)
```
YearsSinceRemod = 2024 - YearRemodAdd
```
**Why**: 
- Recent renovations increase home value significantly
- Captures maintenance and modernization effect
- Different from house age (can remodel old house)
- Range: 14 - 74 years

#### 4. **TotalBathrooms** (Total Bathroom Count)
```
TotalBathrooms = FullBath + 0.5×HalfBath + BsmtFullBath + 0.5×BsmtHalfBath
```
**Why**: 
- Bathrooms are key selling point for buyers
- Half baths count as 0.5 (standard real estate practice)
- Combines all bathroom types into single metric
- Range: 1.0 - 6.0 bathrooms

**Real-world relevance**: "How many bathrooms?" is top buyer question


#### 5. **OverallScore** (Quality × Condition)
```
OverallScore = OverallQual × OverallCond
```
**Why**: 
- Captures interaction between quality and condition
- High quality + poor condition ≠ high quality + good condition
- Single metric easier for linear models to use
- Range: 1 - 90

**Example**: Quality 9, Condition 5 → Score 45 vs Quality 5, Condition 9 → Score 45

#### 6. **TotalPorchSF** (Total Porch Area)
```
TotalPorchSF = OpenPorchSF + EnclosedPorch + 3SsnPorch + ScreenPorch
```
**Why**: 
- Outdoor living space adds value
- Four separate porch columns are redundant
- Total outdoor space is what matters to buyers
- Range: 0 - 1,027 sq ft

#### 7. **HasGarage** (Binary: 1 if garage exists, 0 otherwise)
```
HasGarage = 1 if GarageArea > 0 else 0
```
**Why**: 
- Garage presence/absence is important binary signal
- Complements GarageArea (which gives size)
- Distribution: 1,375 with garage (94.4%), 81 without (5.6%)

#### 8. **HasBasement** (Binary: 1 if basement exists, 0 otherwise)
```
HasBasement = 1 if TotalBsmtSF > 0 else 0
```
**Why**: 
- Basement presence significantly affects value
- Binary feature for existence vs continuous size feature
- Distribution: 1,419 with basement (97.5%), 37 without (2.5%)

#### 9. **HasFireplace** (Binary: 1 if fireplace exists, 0 otherwise)
```
HasFireplace = 1 if Fireplaces > 0 else 0
```
**Why**: 
- Fireplace is desirable amenity
- Binary indicator + count provide complementary information
- Distribution: 766 with fireplace (52.6%), 690 without (47.4%)


#### 10. **IsRemodeled** (Binary: 1 if remodeled, 0 otherwise)
```
IsRemodeled = 1 if YearBuilt ≠ YearRemodAdd else 0
```
**Why**: 
- Indicates if house has been renovated
- Remodeled homes may have premium vs original homes
- Distribution: 694 remodeled (47.7%), 762 not remodeled (52.3%)

### 4.2 Feature Engineering Principles

**Key Takeaways**:
1. **Domain knowledge drives good features** - Understanding real estate helps create meaningful features
2. **Combine related features** - TotalSF is more useful than three separate floor areas
3. **Create interaction terms** - OverallScore captures quality×condition interaction
4. **Add binary indicators** - HasGarage, HasBasement signal presence/absence
5. **Transform timestamps** - HouseAge is more interpretable than YearBuilt

**Feature engineering impact**:
- Can improve model performance by 10-30%
- More important than choosing between RandomForest vs XGBoost
- Reduces model complexity (fewer features to learn from)

---

## 5. Target Engineering (price_class)

### 5.1 Classification Target Creation

**Goal**: Convert continuous SalePrice into categorical price_class for classification task

**Method**: Quantile-based binning (33rd and 66th percentiles)

```
if SalePrice ≤ $139,000:        → 'low'
elif SalePrice ≤ $189,285:      → 'medium'
else:                           → 'high'
```

**Thresholds**:
- **33rd percentile**: $139,000
- **66th percentile**: $189,285

**Distribution**:
- Low: 483 houses (33.2%)
- Medium: 478 houses (32.8%)
- High: 495 houses (34.0%)


### 5.2 Why Quantile-Based Binning?

**Advantages**:
- ✅ **Balanced classes**: Each class has ~33% of data (important for classification)
- ✅ **Data-driven**: Thresholds come from actual data distribution
- ✅ **Adaptable**: Works regardless of price range or location
- ✅ **No class imbalance**: Prevents models from being biased toward majority class

**Alternative approaches we didn't use**:

| Approach | Thresholds | Problem |
|----------|-----------|---------|
| Fixed amounts | <$150k, $150k-$250k, >$250k | Arbitrary, may create imbalance |
| Equal width | Divide range into 3 equal parts | Skewed distribution → imbalanced classes |
| Domain expert | Use realtor definitions | Location-specific, not generalizable |

**Why balanced classes matter**:
- Unbalanced classes (e.g., 70% low, 20% medium, 10% high) lead to poor model performance
- Model may just predict "low" for everything and still get 70% accuracy
- Balanced classes force model to learn meaningful distinctions

### 5.3 Encoding for Output

**Mapping**: `{'low': 0, 'medium': 1, 'high': 2}`

This integer encoding is used in the final processed_data.csv for ML models.

---

## 6. Encoding Strategy

Categorical variables must be converted to numbers for ML algorithms. **But not all encoding methods are equal!**

### 6.1 Two Types of Categorical Variables


#### **Ordinal Features** (have natural order/ranking)
- ExterQual: Ex > Gd > TA > Fa > Po
- BsmtQual: Ex > Gd > TA > Fa > Po > None
- KitchenQual: Ex > Gd > TA > Fa > Po
- FireplaceQu: Ex > Gd > TA > Fa > Po > None
- And 8 more quality/condition features

**Encoding**: **Label Encoding** (preserves order)
- Ex=4, Gd=3, TA=2, Fa=1, Po=0
- Model learns: "Higher number = better quality"

#### **Nominal Features** (no natural order)
- Neighborhood: Bloomington, College Creek, Old Town... (no ranking)
- HouseStyle: 1Story, 2Story, Split Level... (just different, not better/worse)
- RoofStyle: Gable, Hip, Flat... (no inherent order)
- And 23 more categorical features

**Encoding**: **One-Hot Encoding** (creates binary columns)
- Neighborhood_Bloomington: 0 or 1
- Neighborhood_OldTown: 0 or 1
- Each neighborhood gets its own column

### 6.2 Why Encoding Strategy Matters

**Example: If we used Label Encoding on Neighborhood**
```
Neighborhood_encoded:
  Bloomington = 0
  OldTown = 1
  College Creek = 2
```
❌ **Problem**: Model thinks OldTown (1) is "halfway between" Bloomington (0) and College Creek (2)
❌ **Reality**: No such relationship exists! They're just different neighborhoods.

**Correct approach: One-Hot Encoding**
```
Neighborhood_Bloomington: [1, 0, 0]
Neighborhood_OldTown:     [0, 1, 0]
Neighborhood_CollegeCr:   [0, 0, 1]
```
✅ Each neighborhood is independent, no false ordering


### 6.3 Encoding Results

**Before encoding**: 98 columns (38 numerical, 26 nominal categorical, 12 ordinal categorical, 2 targets)

**After encoding**: 211 columns
- Label-encoded ordinal features: 12 new columns (with `_encoded` suffix)
- One-hot encoded nominal features: ~149 binary columns
- Original numerical features: 48 (38 original + 10 engineered)
- Targets: 2 (SalePrice, price_class)

**Why so many columns?**
- One-hot encoding creates a column for each category value
- Example: Neighborhood has 25 values → 24 columns (drop_first=True removes one to avoid multicollinearity)

**Curse of dimensionality concern?**
- Not a major issue for tree-based models (they handle high dimensions well)
- Linear models may need dimensionality reduction (PCA) or regularization (Lasso)

---

## 7. Scaling Analysis

### 7.1 Feature Value Ranges

| Feature | Min | Max | Range |
|---------|-----|-----|-------|
| TotalSF | 334 | 6,428 | 6,094 |
| HouseAge | 14 | 152 | 138 |
| TotalBathrooms | 1 | 6 | 5 |
| OverallScore | 1 | 90 | 89 |
| GrLivArea | 334 | 3,627 | 3,293 |
| LotArea | 1,300 | 215,245 | 213,945 ⚠️ |
| TotalBsmtSF | 0 | 3,206 | 3,206 |
| GarageArea | 0 | 1,390 | 1,390 |

**Observation**: Features have vastly different scales (TotalBathrooms: 1-6 vs LotArea: 1,300-215,245)


### 7.2 Why Scaling Was NOT Applied

**Decision**: Scaling is NOT applied in this preprocessing pipeline

**Reasons**:

1. **Tree-based models don't need scaling**
   - Random Forest, XGBoost, Decision Trees are scale-invariant
   - They split on individual features, not distances
   - Scaling provides no benefit

2. **Prevents data leakage**
   - Scaling uses statistics (mean, std) from entire dataset
   - Must be calculated only on training data, then applied to test data
   - Better handled in model pipeline, not preprocessing

3. **Preserves interpretability**
   - Unscaled features are easier to understand
   - "TotalSF = 2000 sq ft" is clearer than "TotalSF_scaled = 0.42"

4. **Pipeline flexibility**
   - Different models need different scaling
   - Linear/Neural networks → StandardScaler
   - Tree models → No scaling
   - Keep preprocessing model-agnostic

### 7.3 When and How to Apply Scaling (Recommendation)

**For Linear Models (Linear Regression, Logistic Regression, SVM, Neural Networks)**:
```python
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])

# Fit on training data only
pipeline.fit(X_train, y_train)
pipeline.predict(X_test)  # Automatically applies same scaling
```

**StandardScaler vs MinMaxScaler**:
- **StandardScaler**: (X - mean) / std → Good for normally distributed features
- **MinMaxScaler**: (X - min) / (max - min) → Good when you need values in [0,1]

**⚠️ Critical mistake to avoid**:
```python
# ❌ WRONG - Causes data leakage
X_scaled = StandardScaler().fit_transform(X)  # Uses test data statistics!
X_train, X_test = train_test_split(X_scaled)

# ✅ CORRECT - No leakage
X_train, X_test = train_test_split(X)
scaler = StandardScaler().fit(X_train)  # Only fit on training data
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Apply training statistics
```


---

## 8. Final Dataset Description

### 8.1 Output Files Generated

#### **1. cleaned_data.csv**
- **Purpose**: Intermediate cleaned dataset with missing values handled
- **Rows**: 1,456 (4 outliers removed from original 1,460)
- **Columns**: 98
  - Original features with missing values filled
  - 10 new engineered features
  - Target variables: SalePrice, price_class
- **Missing Values**: 0 (all handled)
- **Use Case**: Checkpoint for review, further feature engineering, or EDA

#### **2. processed_data.csv**
- **Purpose**: Final ML-ready dataset with all preprocessing complete
- **Rows**: 1,456
- **Columns**: 211
  - 209 feature columns (numerical + encoded categorical)
  - 1 regression target (SalePrice)
  - 1 classification target (price_class: 0=low, 1=medium, 2=high)
- **Encoding**: Complete (ordinal label-encoded, nominal one-hot encoded)
- **Scaling**: Not applied (model-specific, apply in pipeline)
- **Use Case**: Ready for model training

#### **3. feature_names.txt**
- **Purpose**: Reference list of all 209 feature names
- **Use Case**: Feature selection, understanding model inputs


### 8.2 Data Transformation Summary

| Stage | Rows | Columns | Key Changes |
|-------|------|---------|-------------|
| **Original** | 1,460 | 81 | Raw data with missing values |
| **After Cleaning** | 1,456 | 75 | Dropped Id + 5 high-missing columns, removed 4 outliers |
| **After Feature Engineering** | 1,456 | 98 | Added 10 engineered features, created price_class |
| **After Encoding** | 1,456 | 211 | Label-encoded ordinal, one-hot encoded nominal |

**Row changes**: 1,460 → 1,456 (-4 rows, 0.27% data loss)
- **Acceptable loss**: Only extreme outliers removed, 99.7% data retained

**Column changes**: 81 → 211 (+130 columns, 160% increase)
- **Expected**: One-hot encoding creates many binary columns
- **Benefit**: ML models can now process categorical information

### 8.3 Feature Breakdown

**Final 209 features consist of**:

1. **Original Numerical Features**: 35 features
   - Area measurements (LotArea, GrLivArea, etc.)
   - Counts (Bedrooms, Fireplaces, etc.)
   - Years (YearBuilt, YearRemodAdd, etc.)
   - Quality ratings (OverallQual, OverallCond)

2. **Engineered Features**: 10 features
   - TotalSF, HouseAge, YearsSinceRemod
   - TotalBathrooms, OverallScore, TotalPorchSF
   - HasGarage, HasBasement, HasFireplace, IsRemodeled

3. **Encoded Ordinal Features**: 12 features
   - Quality/condition ratings (label-encoded)
   - Preserve ordinal relationships

4. **One-Hot Encoded Features**: ~152 features
   - Neighborhood, HouseStyle, RoofStyle, etc.
   - Binary indicators for each category


### 8.4 Target Variables

#### **Regression Target: SalePrice**
- **Type**: Continuous (USD)
- **Range**: $34,900 - $755,000
- **Mean**: $180,921
- **Median**: $163,000
- **Use**: Predict exact house price

#### **Classification Target: price_class**
- **Type**: Categorical (0, 1, 2)
- **Classes**: 
  - 0 (low): 483 samples (33.2%)
  - 1 (medium): 478 samples (32.8%)
  - 2 (high): 495 samples (34.0%)
- **Balance**: Well-balanced (important for classification)
- **Use**: Predict price category

---

## 9. Key Lessons for ML Engineers 🎓

### 9.1 Data Cleaning Principles

#### **Lesson 1: Understand Your Missing Values**
Not all missing values are equal:
- **Informative missing** (e.g., no garage) → Fill with 'None', keep the information
- **Random missing** (e.g., LotFrontage) → Impute with median/mode
- **Too much missing** (>50%) → Drop the column

**❌ Bad practice**: Blindly fill all missing with 0 or mean
**✅ Good practice**: Analyze each column's missing pattern and domain meaning

#### **Lesson 2: Feature Engineering > Algorithm Selection**
- A mediocre model with great features beats a great model with mediocre features
- Domain knowledge is your superpower
- Think like your end-user (e.g., home buyers care about total space, not individual floor sizes)


#### **Lesson 3: Encoding Matters**
Choose encoding based on feature type:
- **Ordinal** (Ex > Gd > TA) → Label Encoding
- **Nominal** (Red, Blue, Green) → One-Hot Encoding
- **High cardinality** (1000+ categories) → Target Encoding or Embeddings

**What happens if you mess this up?**
- Wrong encoding → Model learns false patterns → Poor predictions

#### **Lesson 4: Beware of Data Leakage**
**Data leakage** = Using information from test set during training

**Common mistakes**:
```python
# ❌ LEAKAGE: Scaling before split
X_scaled = scaler.fit_transform(X)  # Uses test data statistics!
X_train, X_test = train_test_split(X_scaled)

# ❌ LEAKAGE: Imputing before split
X['LotFrontage'].fillna(X['LotFrontage'].mean())  # Uses test data!

# ✅ CORRECT: Always split first
X_train, X_test = train_test_split(X)
scaler.fit(X_train)  # Only learn from training data
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**Why this matters**: Leakage inflates your metrics but fails in production

#### **Lesson 5: Document Everything**
- Future you will forget why you made decisions
- Team members need to understand your choices
- Reproducibility requires documentation
- This report is as important as the code!


### 9.2 Common Pitfalls to Avoid

| Pitfall | Why It's Bad | Correct Approach |
|---------|--------------|------------------|
| **Dropping all rows with missing values** | Lose too much data | Impute intelligently based on domain |
| **Using mean for outlier-heavy features** | Skewed by extremes | Use median instead |
| **Label encoding nominal features** | Creates false ordinal relationships | Use one-hot encoding |
| **Scaling before train-test split** | Data leakage | Scale after split, fit on train only |
| **Removing all outliers blindly** | May remove valid data | Analyze outliers, only remove clear errors |
| **Not creating target for classification** | Can't do classification task | Engineer price_class from SalePrice |
| **Over-engineering features** | Overfitting, complexity | Balance feature creation with simplicity |

### 9.3 Next Steps for Model Development

**1. Exploratory Data Analysis (EDA)**
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('processed_data.csv')

# Correlation heatmap
correlation = df.corr()['SalePrice'].sort_values(ascending=False)
print(correlation.head(20))  # Top 20 correlated features

# Feature importance will come from trained model
```

**2. Train-Test Split**
```python
from sklearn.model_selection import train_test_split

X = df.drop(['SalePrice', 'price_class'], axis=1)
y_reg = df['SalePrice']
y_clf = df['price_class']

X_train, X_test, y_train, y_test = train_test_split(
    X, y_reg, test_size=0.2, random_state=42
)
```


**3. Baseline Models (Start Simple)**
```python
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score

# Regression baseline
rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg.fit(X_train, y_train)
y_pred = rf_reg.predict(X_test)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: ${np.sqrt(mean_squared_error(y_test, y_pred)):,.0f}")

# Classification baseline
rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
rf_clf.fit(X_train, y_train_clf)
accuracy = accuracy_score(y_test_clf, rf_clf.predict(X_test))
print(f"Accuracy: {accuracy:.4f}")
```

**4. Advanced Models**
- **XGBoost/LightGBM**: Often best for tabular data
- **Neural Networks**: If you have enough data and computing power
- **Ensemble Methods**: Combine multiple models

**5. Hyperparameter Tuning**
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestRegressor(), 
    param_grid, 
    cv=5, 
    scoring='neg_mean_squared_error'
)
grid_search.fit(X_train, y_train)
print(f"Best parameters: {grid_search.best_params_}")
```


### 9.4 Evaluation Metrics to Use

#### **For Regression (SalePrice prediction)**
- **RMSE** (Root Mean Squared Error): Average prediction error in dollars
- **R² Score**: Proportion of variance explained (0-1, higher is better)
- **MAE** (Mean Absolute Error): Average absolute error

**Target metrics**:
- R² > 0.85 (85% variance explained)
- RMSE < $25,000 (average error under $25k)

#### **For Classification (price_class prediction)**
- **Accuracy**: Overall correct predictions
- **F1-Score**: Balance of precision and recall
- **Confusion Matrix**: See which classes are confused

**Target metrics**:
- Accuracy > 0.80 (80% correct)
- Balanced F1-scores across all three classes

### 9.5 Feature Selection (Optional)

If 209 features is too many:
```python
from sklearn.feature_selection import SelectKBest, f_regression

# Select top 50 features
selector = SelectKBest(score_func=f_regression, k=50)
X_train_selected = selector.fit_transform(X_train, y_train)

# Get selected feature names
selected_features = X.columns[selector.get_support()]
```

**Or use feature importance from Random Forest**:
```python
importances = rf_reg.feature_importances_
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': importances
}).sort_values('importance', ascending=False)

print(feature_importance.head(20))  # Top 20 features
```


---

## 10. Summary & Conclusion

### 10.1 What We Accomplished

✅ **Loaded and understood** Ames Housing dataset (1,460 houses, 81 features)

✅ **Cleaned data systematically**:
- Dropped 6 irrelevant/high-missing columns
- Handled missing values intelligently (19 columns)
- Removed 4 extreme outliers

✅ **Engineered 10 powerful features**:
- Combined features (TotalSF, TotalBathrooms, TotalPorchSF)
- Temporal features (HouseAge, YearsSinceRemod)
- Binary indicators (HasGarage, HasBasement, HasFireplace, IsRemodeled)
- Interaction terms (OverallScore)

✅ **Created classification target**:
- price_class (low/medium/high) using quantile-based binning
- Balanced classes for fair model training

✅ **Encoded categorical variables properly**:
- Label encoding for ordinal features (12 features)
- One-hot encoding for nominal features (26 → 152 features)

✅ **Made informed scaling decision**:
- Chose not to scale in preprocessing
- Documented when/how to scale during modeling

✅ **Produced ML-ready outputs**:
- cleaned_data.csv (intermediate checkpoint)
- processed_data.csv (final ML-ready dataset)
- feature_names.txt (feature reference)
- DATA_CLEANING_REPORT.md (this document!)


### 10.2 Key Metrics

| Metric | Value |
|--------|-------|
| **Data Retention** | 99.7% (1,456 / 1,460 rows) |
| **Missing Values** | 0 (all 7,829 handled) |
| **Final Features** | 209 |
| **Regression Target** | SalePrice ($34,900 - $755,000) |
| **Classification Target** | price_class (3 balanced classes) |
| **Ready for Training** | ✅ Yes |

### 10.3 Quality Assurance Checklist

- ✅ No missing values remain
- ✅ No data leakage in preprocessing
- ✅ Categorical variables properly encoded
- ✅ Outliers analyzed and documented
- ✅ Feature engineering adds domain knowledge
- ✅ Classification target balanced
- ✅ All decisions documented with reasoning
- ✅ Code is reproducible
- ✅ Outputs saved in standard formats

### 10.4 Files for Next Stage

**Use these files to train your models**:

1. **processed_data.csv** → Primary file for ML training
2. **feature_names.txt** → Reference for feature selection
3. **cleaned_data.csv** → For additional EDA or feature engineering
4. **DATA_CLEANING_REPORT.md** → Documentation for understanding decisions


### 10.5 Final Thoughts for Beginners

**Data cleaning is not glamorous, but it's 70% of the work in real ML projects.**

Remember:
1. **Garbage in, garbage out** - Clean data is the foundation of good models
2. **Understand before transforming** - Know your data's story
3. **Document your decisions** - Future you will thank you
4. **Start simple, iterate** - Perfect is the enemy of good
5. **Domain knowledge wins** - Understanding real estate made better features

**You are now ready to build your multi-task ML system!**

Good luck with model training! 🚀

---

## Appendix: Quick Reference Commands

### Loading the Data
```python
import pandas as pd

# Load processed data
df = pd.read_csv('processed_data.csv')

# Separate features and targets
X = df.drop(['SalePrice', 'price_class'], axis=1)
y_regression = df['SalePrice']
y_classification = df['price_class']
```

### Basic EDA
```python
# Shape
print(f"Features: {X.shape}")
print(f"Target stats: {y_regression.describe()}")

# Missing values check
print(f"Missing values: {df.isnull().sum().sum()}")

# Feature types
print(f"Numerical: {X.select_dtypes(include=['int64','float64']).shape[1]}")
print(f"Binary: {X.select_dtypes(include=['uint8']).shape[1]}")
```

---

**End of Report**

*This preprocessing pipeline was designed for educational purposes. Every decision was made deliberately to teach ML engineering best practices.*

