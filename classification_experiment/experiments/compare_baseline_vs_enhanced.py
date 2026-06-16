"""
Comparison Analysis: Baseline vs Enhanced Dataset
==================================================

Compare classification results between:
- Baseline: Original Dataset A (209 features)
- Enhanced: Dataset A with feature engineering (214 features)
"""

import pandas as pd
import json

print("=" * 80)
print("CLASSIFICATION EXPERIMENT: BASELINE VS ENHANCED COMPARISON")
print("=" * 80)
print()

# Load baseline results
with open('logistic_results.json', 'r') as f:
    lr_baseline = json.load(f)

with open('random_forest_results.json', 'r') as f:
    rf_baseline = json.load(f)

with open('xgboost_results.json', 'r') as f:
    xgb_baseline = json.load(f)

# Load enhanced results
with open('logistic_results_enhanced.json', 'r') as f:
    lr_enhanced = json.load(f)

with open('random_forest_results_enhanced.json', 'r') as f:
    rf_enhanced = json.load(f)

with open('xgboost_results_enhanced.json', 'r') as f:
    xgb_enhanced = json.load(f)

print("✓ All results loaded")
print()

# Create comparison table
print("=" * 80)
print("F1-MACRO SCORE COMPARISON (Primary Metric)")
print("=" * 80)
print()

models = ['Logistic Regression', 'Random Forest', 'XGBoost']
baseline_scores = [
    lr_baseline['test_f1_macro'],
    rf_baseline['test_f1_macro'],
    xgb_baseline['test_f1_macro']
]
enhanced_scores = [
    lr_enhanced['test_f1_macro'],
    rf_enhanced['test_f1_macro'],
    xgb_enhanced['test_f1_macro']
]
improvements = [
    enhanced_scores[i] - baseline_scores[i] for i in range(3)
]
improvement_pct = [
    (improvements[i] / baseline_scores[i]) * 100 for i in range(3)
]

print(f"{'Model':<25} {'Baseline':>10} {'Enhanced':>10} {'Change':>10} {'% Change':>10}")
print("-" * 80)
for i, model in enumerate(models):
    direction = "📈" if improvements[i] > 0 else "📉" if improvements[i] < 0 else "➡️"
    print(f"{model:<25} {baseline_scores[i]:>10.4f} {enhanced_scores[i]:>10.4f} "
          f"{improvements[i]:>+10.4f} {improvement_pct[i]:>+9.2f}% {direction}")

print()

# Accuracy comparison
print("=" * 80)
print("ACCURACY COMPARISON")
print("=" * 80)
print()

baseline_acc = [
    lr_baseline['test_accuracy'],
    rf_baseline['test_accuracy'],
    xgb_baseline['test_accuracy']
]
enhanced_acc = [
    lr_enhanced['test_accuracy'],
    rf_enhanced['test_accuracy'],
    xgb_enhanced['test_accuracy']
]
acc_improvements = [
    enhanced_acc[i] - baseline_acc[i] for i in range(3)
]
acc_improvement_pct = [
    (acc_improvements[i] / baseline_acc[i]) * 100 for i in range(3)
]

print(f"{'Model':<25} {'Baseline':>10} {'Enhanced':>10} {'Change':>10} {'% Change':>10}")
print("-" * 80)
for i, model in enumerate(models):
    direction = "📈" if acc_improvements[i] > 0 else "📉" if acc_improvements[i] < 0 else "➡️"
    print(f"{model:<25} {baseline_acc[i]:>10.4f} {enhanced_acc[i]:>10.4f} "
          f"{acc_improvements[i]:>+10.4f} {acc_improvement_pct[i]:>+9.2f}% {direction}")

print()

# Model rankings
print("=" * 80)
print("MODEL RANKINGS (by F1-Macro)")
print("=" * 80)
print()

baseline_ranking = sorted(zip(models, baseline_scores), key=lambda x: x[1], reverse=True)
enhanced_ranking = sorted(zip(models, enhanced_scores), key=lambda x: x[1], reverse=True)

print("BASELINE DATASET:")
for rank, (model, score) in enumerate(baseline_ranking, 1):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
    print(f"  {medal} {rank}. {model:<25} F1-Macro: {score:.4f}")

print()
print("ENHANCED DATASET:")
for rank, (model, score) in enumerate(enhanced_ranking, 1):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
    print(f"  {medal} {rank}. {model:<25} F1-Macro: {score:.4f}")

print()

# Ranking changes
print("RANKING CHANGES:")
baseline_ranks = {model: rank+1 for rank, (model, _) in enumerate(baseline_ranking)}
enhanced_ranks = {model: rank+1 for rank, (model, _) in enumerate(enhanced_ranking)}

for model in models:
    base_rank = baseline_ranks[model]
    enh_rank = enhanced_ranks[model]
    if base_rank == enh_rank:
        change = "No change"
    elif base_rank > enh_rank:
        change = f"Improved from #{base_rank} to #{enh_rank}"
    else:
        change = f"Dropped from #{base_rank} to #{enh_rank}"
    print(f"  {model:<25} {change}")

print()

# Per-class F1 comparison
print("=" * 80)
print("PER-CLASS F1 SCORE COMPARISON")
print("=" * 80)
print()

for i, model in enumerate(models):
    print(f"{model}:")
    if i == 0:
        base_f1 = lr_baseline['f1_per_class']
        enh_f1 = lr_enhanced['f1_per_class']
    elif i == 1:
        base_f1 = rf_baseline['f1_per_class']
        enh_f1 = rf_enhanced['f1_per_class']
    else:
        base_f1 = xgb_baseline['f1_per_class']
        enh_f1 = xgb_enhanced['f1_per_class']
    
    for cls in range(3):
        change = enh_f1[cls] - base_f1[cls]
        direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"  Class {cls}: {base_f1[cls]:.4f} → {enh_f1[cls]:.4f} "
              f"({change:+.4f}) {direction}")
    print()

# Feature importance analysis (for tree models)
print("=" * 80)
print("FEATURE IMPORTANCE ANALYSIS")
print("=" * 80)
print()

print("RANDOM FOREST:")
print("  Top 3 Baseline Features:")
for i, feat in enumerate(rf_baseline['top_features'][:3], 1):
    print(f"    {i}. {feat['feature']:<30} {feat['importance']:.6f}")
print()
print("  Top 3 Enhanced Features:")
for i, feat in enumerate(rf_enhanced['top_features'][:3], 1):
    marker = " ⭐ NEW!" if feat['feature'] in ['TotalSF_x_OverallQual', 'TotalSF_log', 'LotArea_log'] else ""
    print(f"    {i}. {feat['feature']:<30} {feat['importance']:.6f}{marker}")
print()

print("XGBOOST:")
print("  Top 3 Baseline Features:")
for i, feat in enumerate(xgb_baseline['top_features'][:3], 1):
    print(f"    {i}. {feat['feature']:<30} {feat['importance']:.6f}")
print()
print("  Top 3 Enhanced Features:")
for i, feat in enumerate(xgb_enhanced['top_features'][:3], 1):
    marker = " ⭐ NEW!" if feat['feature'] in ['TotalSF_x_OverallQual', 'TotalSF_log', 'LotArea_log'] else ""
    print(f"    {i}. {feat['feature']:<30} {feat['importance']:.6f}{marker}")
print()

# Summary insights
print("=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print()

# Who improved, who declined
improved = [models[i] for i in range(3) if improvements[i] > 0]
declined = [models[i] for i in range(3) if improvements[i] < 0]

print("1. PERFORMANCE CHANGES:")
if improved:
    print(f"   ✅ Improved: {', '.join(improved)}")
if declined:
    print(f"   ❌ Declined: {', '.join(declined)}")
print()

# Best improvement
best_improvement_idx = improvement_pct.index(max(improvement_pct))
worst_improvement_idx = improvement_pct.index(min(improvement_pct))

print("2. BIGGEST IMPACT:")
print(f"   📈 Best improvement: {models[best_improvement_idx]} "
      f"({improvement_pct[best_improvement_idx]:+.2f}%)")
print(f"   📉 Worst performance: {models[worst_improvement_idx]} "
      f"({improvement_pct[worst_improvement_idx]:+.2f}%)")
print()

# Overall winner
print("3. OVERALL WINNER:")
winner_baseline = baseline_ranking[0]
winner_enhanced = enhanced_ranking[0]
print(f"   Baseline: {winner_baseline[0]} (F1: {winner_baseline[1]:.4f})")
print(f"   Enhanced: {winner_enhanced[0]} (F1: {winner_enhanced[1]:.4f})")
if winner_baseline[0] == winner_enhanced[0]:
    print(f"   ✅ Same winner on both datasets")
else:
    print(f"   ⚠️ Winner changed!")
print()

# New features impact
print("4. NEW FEATURES IMPACT:")
print("   TotalSF_x_OverallQual became #1 feature for both RF and XGBoost")
print("   All 3 new features appear in top 15 for Random Forest")
print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
