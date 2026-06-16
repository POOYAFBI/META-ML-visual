import pandas as pd
import numpy as np

df = pd.read_csv('../../data/processed_data.csv')
X = df.drop(['SalePrice', 'price_class'], axis=1)

print("NaN count:", X.isna().sum().sum())
print("Inf count:", np.isinf(X.select_dtypes(include=['float64', 'float32'])).sum().sum())

if X.isna().sum().sum() > 0:
    print("\nColumns with NaN:")
    nan_cols = X.columns[X.isna().any()].tolist()
    for col in nan_cols:
        print(f"  {col}: {X[col].isna().sum()} NaNs")
