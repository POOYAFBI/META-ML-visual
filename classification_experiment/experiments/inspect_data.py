import pandas as pd

# Load processed dataset
df = pd.read_csv('../../data/processed_data.csv')

print(f'Shape: {df.shape}')
print(f'\nColumns (first 30):')
for i, col in enumerate(df.columns[:30]):
    print(f'  {i+1}. {col}')
    
print(f'\nHas price_class: {"price_class" in df.columns}')
print(f'Has TotalSF: {"TotalSF" in df.columns}')
print(f'Has OverallQual: {"OverallQual" in df.columns}')
print(f'Has LotArea: {"LotArea" in df.columns}')

# Check for TotalSF-like features
print(f'\nColumns containing "SF":')
sf_cols = [col for col in df.columns if 'SF' in col.upper()]
for col in sf_cols:
    print(f'  - {col}')
