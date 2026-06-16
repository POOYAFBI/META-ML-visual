"""
Quick Model Comparison Script
==============================
Loads all results and creates side-by-side comparison
"""

import json
import pandas as pd

print("=" * 70)
print("CLASSIFICATION EXPERIMENT - MODEL COMPARISON")
print("=" * 70)
print()

# Load results
with open('logistic_results.json', 'r') as f:
    lr_results = json.load(f)

with open('random_forest_results.json', 'r') as f:
    rf_results = json.load(f)

with open('xgboost_results.json', 'r') as f:
    xgb_results = json.load(f)

# Create comparison table
results_df = pd.DataFrame({
    'Model': ['Logistic Regression', 'Random Forest', 'XGBoost'],
    'Train Accuracy': [
        lr_results['train_accuracy'],
        rf_results['train_accuracy'],
        xgb_results['train_accuracy']
    ],
    'Test Accuracy': [
        lr_results['test_accuracy'],
        rf_results['test_accuracy'],
        xgb_results['test_accuracy']
    ],
    'Train F1-Macro': [
        lr_results['train_f1_macro'],
        rf_results['train_f1_macro'],
        xgb_results['train_f1_macro']
    ],
    'Test F1-Macro': [
        lr_results['test_f1_macro'],
        rf_results['test_f1_macro'],
        xgb_results['test_f1_macro']
    ]
})

# Sort by Test F1-Macro (primary metric)
results_df = results_df.sort_values('Test F1-Macro', ascending=False)

print("TEST SET PERFORMANCE (PRIMARY RANKING)")
print("-" * 70)
print(results_df[['Model', 'Test F1-Macro', 'Test Accuracy']].to_string(index=False))
print()

print("\nTRAINING SET PERFORMANCE")
print("-" * 70)
print(results_df[['Model', 'Train F1-Macro', 'Train Accuracy']].to_string(index=False))
print()

print("\nOVERFITTING ANALYSIS")
print("-" * 70)
for _, row in results_df.iterrows():
    gap = row['Train F1-Macro'] - row['Test F1-Macro']
    print(f"{row['Model']:25s}: F1 gap = {gap:.4f} ({gap*100:.2f}%)")
print()

print("\nPER-CLASS F1-SCORES (Test Set)")
print("-" * 70)
print(f"{'Model':<25s} {'Low':>10s} {'Medium':>10s} {'High':>10s}")
print("-" * 70)
for model_name, results in [
    ('Logistic Regression', lr_results),
    ('Random Forest', rf_results),
    ('XGBoost', xgb_results)
]:
    f1_low, f1_med, f1_high = results['f1_per_class']
    print(f"{model_name:<25s} {f1_low:>10.4f} {f1_med:>10.4f} {f1_high:>10.4f}")
print()

print("\nFINAL RANKING (by Test F1-Macro)")
print("=" * 70)
for i, (_, row) in enumerate(results_df.iterrows(), 1):
    medal = ["🥇", "🥈", "🥉"][i-1]
    print(f"{medal} {i}. {row['Model']:<25s} F1-Macro: {row['Test F1-Macro']:.4f}")
print()

winner = results_df.iloc[0]
print(f"WINNER: {winner['Model']} ⭐")
print(f"  F1-Macro: {winner['Test F1-Macro']:.4f}")
print(f"  Accuracy: {winner['Test Accuracy']:.4f} ({winner['Test Accuracy']*100:.2f}%)")
print()
print("=" * 70)
