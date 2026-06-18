# Model Internal Analysis

## 1. Model Overview

This audit inspected the two persisted regression Linear Regression artifacts because they are the most suspicious `.pkl` files for report/runtime divergence:

| Artifact | Dataset file used by persistence script | Model type | Parameters | `n_features_in_` | `feature_names_in_` | Feature JSON count | Dataset feature count |
|---|---|---:|---|---:|---:|---:|---:|
| `models/regression/baseline_dataset/linear_regression.pkl` | `data/processed_data.csv` | `sklearn.linear_model._base.LinearRegression` | `copy_X=True`, `fit_intercept=True`, `n_jobs=None`, `positive=False`, `tol=1e-06` | 209 | absent | 209 | 209 |
| `models/regression/enhanced_dataset/linear_regression.pkl` | `data/processed_data_minimal_fe.csv` | `sklearn.linear_model._base.LinearRegression` | `copy_X=True`, `fit_intercept=True`, `n_jobs=None`, `positive=False`, `tol=1e-06` | 199 | absent | 199 | 199 |

Important internal observation: both saved models were trained on NumPy arrays rather than pandas DataFrames in the persistence pipeline. Therefore, the internal `feature_names_in_` attribute is absent even though `n_features_in_` is correct. The feature names are externalized in the adjacent `*_features.json` files, and runtime prediction depends entirely on that external JSON order being used exactly.

The saved Linear Regression intercepts are:

| Artifact | Intercept |
|---|---:|
| baseline Linear Regression | -54,015.103985729686 |
| enhanced/minimal-FE Linear Regression | -579,042.736217862 |

## 2. Coefficient Analysis

### Baseline Linear Regression (`209` coefficients)

Coefficient distribution:

| Statistic | Value |
|---|---:|
| min | -122,901.07468097979 |
| max | 37,351.82216716353 |
| mean | -2,175.2816887066883 |
| median | 2.1464074961841106e-10 |
| standard deviation | 17,275.998340798695 |
| exactly zero coefficients | 0 |
| near-zero coefficients, `abs(coef) < 1e-9` | 3 |

Top absolute coefficients in the saved artifact:

| Rank | Feature | Coefficient |
|---:|---|---:|
| 1 | `Condition2_RRAe` | -122,901.07468097979 |
| 2 | `Functional_Sev` | -74,690.52813483159 |
| 3 | `Condition2_PosN` | -56,700.52805779176 |
| 4 | `LandSlope_Sev` | -51,532.628375690256 |
| 5 | `RoofStyle_Gable` | -48,128.43361269007 |
| 6 | `RoofStyle_Gambrel` | -46,474.483417562 |
| 7 | `RoofStyle_Hip` | -46,024.74279627817 |
| 8 | `Neighborhood_StoneBr` | 37,351.82216716353 |
| 9 | `RoofStyle_Shed` | 37,256.67231511951 |
| 10 | `HasBasement` | -35,405.124597149166 |

Abnormal finding: the largest weights are sparse one-hot indicators and engineered binary flags, not stable continuous predictors. This does not prove file corruption, because the same coefficients are reproduced by retraining, but it does prove that predictions are highly sensitive to exact one-hot/binary feature presence and order. For example, `RoofStyle_Gable=1` alone subtracts about `$48,128`, and `HasBasement=1` alone subtracts about `$35,405` in the baseline model.

### Enhanced/minimal-FE Linear Regression (`199` coefficients)

Coefficient distribution:

| Statistic | Value |
|---|---:|
| min | -123,308.89289587003 |
| max | 38,302.24217700761 |
| mean | -3,136.568844382608 |
| median | 0.12121921895436572 |
| standard deviation | 17,572.568205626012 |
| exactly zero coefficients | 0 |
| near-zero coefficients, `abs(coef) < 1e-9` | 3 |

Top absolute coefficients in the saved artifact:

| Rank | Feature | Coefficient |
|---:|---|---:|
| 1 | `Condition2_RRAe` | -123,308.89289587003 |
| 2 | `Functional_Sev` | -75,052.94427103267 |
| 3 | `Condition2_PosN` | -59,789.77952185455 |
| 4 | `Heating_OthW` | -51,828.924412574284 |
| 5 | `RoofStyle_Gable` | -47,111.133734654795 |
| 6 | `LandSlope_Sev` | -46,115.34503590338 |
| 7 | `RoofStyle_Gambrel` | -44,971.49282300386 |
| 8 | `RoofStyle_Hip` | -44,794.423160776496 |
| 9 | `SaleType_New` | 38,302.24217700761 |
| 10 | `Neighborhood_StoneBr` | 36,563.43110491871 |

Abnormal finding: the enhanced/minimal-FE model also contains very large sparse-category coefficients. The much more negative intercept is internally offset by very large positive year-based contributions (`YearBuilt`, `YearRemodAdd`, and `GarageYrBlt`). Therefore, missing or zeroed date fields will catastrophically depress predictions.

## 3. Feature Alignment Check

Feature alignment was verified at three levels:

1. saved model expected feature count, via `n_features_in_`;
2. external runtime feature list, via `linear_regression_features.json`;
3. dataset training order, via the CSV columns after dropping `SalePrice` and `price_class`.

| Artifact | Model feature count equals JSON count | JSON order equals dataset training order | Missing names | Extra names | Verdict |
|---|---:|---:|---:|---:|---|
| baseline Linear Regression | yes, `209 == 209` | yes | 0 | 0 | aligned |
| enhanced/minimal-FE Linear Regression | yes, `199 == 199` | yes | 0 | 0 | aligned |

Exact mismatch result: no feature-name mismatch and no feature-order mismatch were found between the persisted JSON feature lists and the corresponding training datasets.

However, the model object itself does **not** retain `feature_names_in_`. That means the `.pkl` cannot internally validate that incoming columns are semantically correct. If runtime supplies a raw NumPy vector, the saved model only checks vector length. Correct semantics are guaranteed only if the external JSON order is used exactly.

## 4. Sample Prediction Breakdown

The inspected sample is row `0` from each corresponding regression dataset. The prediction was computed as:

```text
prediction = intercept + sum(coef_i * feature_i)
```

### Baseline sample row `0`

| Quantity | Value |
|---|---:|
| actual `SalePrice` | 208,500 |
| saved-model prediction | 214,759.34864239913 |
| intercept | -54,015.103985729686 |
| sum of feature contributions | 268,774.4526281288 |

Top absolute feature contributions:

| Rank | Feature | Input value | Coefficient | Contribution |
|---:|---|---:|---:|---:|
| 1 | `YearBuilt` | 2003 | 151.87611161334786 | 304,207.8515615358 |
| 2 | `YrSold` | 2008 | -128.12343324718165 | -257,271.85396034076 |
| 3 | `GarageYrBlt` | 2003.0 | 40.91681584726575 | 81,956.3821420733 |
| 4 | `OverallScore` | 35 | 1,634.7553755630315 | 57,216.4381447061 |
| 5 | `TotalSF` | 2566 | 21.162498762901123 | 54,302.97182560428 |
| 6 | `RoofStyle_Gable` | 1 | -48,128.43361269007 | -48,128.43361269007 |
| 7 | `GrLivArea` | 1710 | 21.753863945583362 | 37,199.10734694755 |
| 8 | `HasBasement` | 1 | -35,405.124597149166 | -35,405.124597149166 |
| 9 | `YearRemodAdd` | 2003 | 15.343300909403816 | 30,732.631721535843 |
| 10 | `Street_Pave` | 1 | 26,049.625256593696 | 26,049.625256593696 |

Explanation: this prediction is dominated by cancellation between large year terms. `YearBuilt` contributes about `+$304k`, while `YrSold` contributes about `-$257k`. This is internally consistent with the saved model, but it also means predictions become much worse if year-like fields are absent, zeroed, or semantically shifted.

### Enhanced/minimal-FE sample row `0`

| Quantity | Value |
|---|---:|
| actual `SalePrice` | 208,500 |
| saved-model prediction | 215,697.73558489012 |
| intercept | -579,042.736217862 |
| sum of feature contributions | 794,740.4718027525 |

Top absolute feature contributions:

| Rank | Feature | Input value | Coefficient | Contribution |
|---:|---|---:|---:|---:|
| 1 | `YearBuilt` | 2003 | 264.67590271618 | 530,145.8331405086 |
| 2 | `YrSold` | 2008 | -62.71262253685518 | -125,926.9460540052 |
| 3 | `YearRemodAdd` | 2003 | 57.11026254462187 | 114,391.8558768776 |
| 4 | `GarageYrBlt` | 2003.0 | 50.30425868283237 | 100,759.43014171324 |
| 5 | `GrLivArea` | 1710 | 35.22522022729595 | 60,235.126588676074 |
| 6 | `OverallQual` | 7 | 7,081.307855581616 | 49,569.154989071314 |
| 7 | `RoofStyle_Gable` | 1 | -47,111.133734654795 | -47,111.133734654795 |
| 8 | `Street_Pave` | 1 | 29,946.13636404603 | 29,946.13636404603 |
| 9 | `TotRmsAbvGrd` | 8 | 3,175.002182373107 | 25,400.017458984858 |
| 10 | `OverallCond` | 5 | 5,076.495557097618 | 25,382.47778548809 |

Explanation: the enhanced/minimal-FE artifact is even more dependent on very large offsetting terms. The model starts at about `-$579k`; the date fields then add about `+$745k` before other features are considered. This is why zero-filled or omitted date values make runtime outputs much worse than report metrics.

## 5. Comparison with Re-trained Model

A fresh Linear Regression model was retrained for each dataset using the same persistence-script logic:

- same CSV file;
- same dropped columns: `SalePrice`, `price_class`;
- same train/test split: `test_size=0.2`, `random_state=42`;
- same unscaled `LinearRegression()` estimator;
- same NumPy-array fitting path as persistence.

### Baseline retrain comparison

| Metric | Saved artifact | Re-trained model | Difference |
|---|---:|---:|---:|
| test RMSE | 22,949.23794173225 | 22,949.23794173158 | ~0.00000000067 |
| test R² | 0.8996521449187238 | 0.8996521449187298 | ~-0.000000000000006 |
| max absolute coefficient difference | — | — | 2.7370480211175163e-06 |
| mean absolute coefficient difference | — | — | 1.1974294501828482e-07 |
| intercept difference, saved minus retrained | — | — | -0.006061193940695375 |
| max absolute prediction difference on test split | — | — | 7.922062650322914e-08 |
| mean absolute prediction difference on test split | — | — | 5.761960406519778e-09 |

### Enhanced/minimal-FE retrain comparison

| Metric | Saved artifact | Re-trained model | Difference |
|---|---:|---:|---:|
| test RMSE | 23,210.430797398363 | 23,210.43079739852 | ~-0.00000000016 |
| test R² | 0.8973549622374428 | 0.8973549622374414 | ~0.0000000000000014 |
| max absolute coefficient difference | — | — | 1.6678620795573806e-07 |
| mean absolute coefficient difference | — | — | 4.769285295000299e-09 |
| intercept difference, saved minus retrained | — | — | -4.1979365050792694e-07 |
| max absolute prediction difference on test split | — | — | 5.878973752260208e-08 |
| mean absolute prediction difference on test split | — | — | 5.942364287090628e-09 |

Critical result: the saved `.pkl` artifacts reproduce the re-trained models to floating-point tolerance. There is no evidence that the Linear Regression `.pkl` files are corrupted, overwritten with the wrong estimator, trained on the wrong feature order, or trained with a materially different split.

The persisted report values are rounded versions of these exact metrics. For example, the baseline artifact's exact test R² is `0.8996521449187238`, which rounds to `0.8997`; the enhanced/minimal-FE artifact's exact test R² is `0.8973549622374428`, which rounds to `0.8974`.

## 6. Root Cause (MOST IMPORTANT)

The exact internal issue is **not coefficient drift between the saved artifact and the training script**. The saved Linear Regression models are internally the same as freshly re-trained models under the persistence pipeline.

The exact internal difference that matters is this:

> The saved `.pkl` models contain only positional coefficients (`coef_`) and `n_features_in_`; they do **not** contain `feature_names_in_` and therefore cannot internally verify feature identity. The runtime semantic mapping is external to the model object and lives in `linear_regression_features.json`.

This leads to worse predictions whenever runtime inputs are incomplete, zero-filled, or not transformed identically to the training matrices. The model internals prove why: many large coefficients multiply fields that must be present and correctly encoded. In the baseline model, `YearBuilt=2003` contributes `+$304,207.85`, `YrSold=2008` contributes `-$257,271.85`, `RoofStyle_Gable=1` contributes `-$48,128.43`, and `HasBasement=1` contributes `-$35,405.12`. In the enhanced/minimal-FE model, the intercept is `-$579,042.74`, and the correct prediction depends on date fields adding back about `+$745k`. If these fields are missing and coerced to zero, the prediction is not a training-report prediction; it is a different feature vector being passed through a model that has no internal feature-name guard.

Verified possible causes:

| Possible cause | Evidence | Verdict |
|---|---|---|
| different feature scaling | Linear Regression artifacts were trained unscaled; retraining unscaled reproduces coefficients and metrics. | not the cause |
| different preprocessing inside saved `.pkl` | `.pkl` contains a bare `LinearRegression`, not a preprocessing pipeline. Preprocessing is external. | external preprocessing dependency confirmed |
| different dataset version | Current CSVs reproduce the saved artifacts and rounded report metrics. | not supported |
| corrupted or overwritten model | Re-trained coefficients/predictions match saved artifacts to floating-point tolerance. | no evidence |
| feature-name/order mismatch between JSON and dataset | JSON feature lists exactly match dataset column order after dropping targets. | no mismatch found |
| runtime incomplete/zero-filled features | Model has no internal name guard, and dominant terms require full engineered/encoded feature vector. | proven risk and direct explanation for worse runtime predictions |

## 7. Final Verdict

The saved Linear Regression `.pkl` files are not internally corrupted and do not materially differ from re-trained models using the same persistence pipeline. They perform worse outside the training report when the input vector is not the same fully preprocessed, fully encoded, correctly ordered feature vector used during training. The decisive internal evidence is that the models store large positional coefficients but no `feature_names_in_`; therefore they cannot detect semantic feature omissions or misalignment. Because the predictions are dominated by large offsetting contributions from year fields, sparse one-hot indicators, and engineered binary flags, any runtime zero-filling or incomplete preprocessing changes the mathematical input and produces worse predictions than the reported test metrics.
