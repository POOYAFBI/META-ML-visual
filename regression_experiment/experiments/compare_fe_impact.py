"""
Feature Engineering Impact Comparison Script
============================================
This script compares model performance between Full FE and Minimal FE datasets
to calculate Feature Engineering Impact Scores.

Usage: Update the results dictionaries below with actual values after training,
       then run this script to generate the comparative analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# STEP 1: INPUT YOUR RESULTS HERE
# ============================================================================

# Full FE Dataset Results (from previous training)
full_fe_results = {
    'Linear Regression': {
        'RMSE': None,  # TODO: Fill in from LINEAR_TRAINING_SUMMARY.md
        'R2': None,    # TODO: Fill in
        'MAE': None,   # TODO: Fill in
        'Accuracy': None,  # TODO: Fill in
        'F1_Score': None   # TODO: Fill in
    },
    'Random Forest': {
        'RMSE': None,  # TODO: Fill in from RF_TRAINING_SUMMARY.md
        'R2': None,    # TODO: Fill in
        'MAE': None,   # TODO: Fill in
        'Accuracy': None,  # TODO: Fill in
        'F1_Score': None   # TODO: Fill in
    },
    'XGBoost': {
        'RMSE': None,  # TODO: Fill in from XGB_TRAINING_SUMMARY.md
        'R2': None,    # TODO: Fill in
        'MAE': None,   # TODO: Fill in
        'Accuracy': None,  # TODO: Fill in
        'F1_Score': None   # TODO: Fill in
    }
}

# Minimal FE Dataset Results (after training on minimal FE)
minimal_fe_results = {
    'Linear Regression': {
        'RMSE': None,  # TODO: Fill in after training
        'R2': None,    # TODO: Fill in
        'MAE': None,   # TODO: Fill in
        'Accuracy': None,  # TODO: Fill in
        'F1_Score': None   # TODO: Fill in
    },
    'Random Forest': {
        'RMSE': None,  # TODO: Fill in after training
        'R2': None,    # TODO: Fill in
        'MAE': None,   # TODO: Fill in
        'Accuracy': None,  # TODO: Fill in
        'F1_Score': None   # TODO: Fill in
    },
    'XGBoost': {
        'RMSE': None,  # TODO: Fill in after training
        'R2': None,    # TODO: Fill in
        'MAE': None,   # TODO: Fill in
        'Accuracy': None,  # TODO: Fill in
        'F1_Score': None   # TODO: Fill in
    }
}

# ============================================================================
# STEP 2: CHECK IF RESULTS ARE FILLED IN
# ============================================================================

def check_results_filled():
    """Check if all results are filled in."""
    all_filled = True
    for model_name in full_fe_results:
        for metric in full_fe_results[model_name]:
            if full_fe_results[model_name][metric] is None:
                print(f"⚠️  Missing: Full FE - {model_name} - {metric}")
                all_filled = False
            if minimal_fe_results[model_name][metric] is None:
                print(f"⚠️  Missing: Minimal FE - {model_name} - {metric}")
                all_filled = False
    return all_filled

print("=" * 80)
print("FEATURE ENGINEERING IMPACT ANALYSIS")
print("=" * 80)

if not check_results_filled():
    print("\n❌ ERROR: Not all results are filled in!")
    print("   Please update the results dictionaries in this script with actual values.")
    print("   Then run this script again.")
    exit(1)

print("\n✓ All results filled in. Proceeding with analysis...")

# ============================================================================
# STEP 3: CALCULATE FE IMPACT SCORES
# ============================================================================

print("\n" + "=" * 80)
print("CALCULATING FE IMPACT SCORES")
print("=" * 80)

# Calculate impact scores
# For RMSE and MAE: lower is better, so positive impact means minimal FE performed worse
# For R2, Accuracy, F1: higher is better, so positive impact means minimal FE performed worse

fe_impact_scores = {}

for model_name in full_fe_results:
    fe_impact_scores[model_name] = {}
    
    # RMSE Impact (higher RMSE in minimal FE = positive impact score)
    full_rmse = full_fe_results[model_name]['RMSE']
    minimal_rmse = minimal_fe_results[model_name]['RMSE']
    fe_impact_scores[model_name]['RMSE_Impact'] = ((minimal_rmse - full_rmse) / full_rmse) * 100
    
    # R2 Impact (lower R2 in minimal FE = positive impact score)
    full_r2 = full_fe_results[model_name]['R2']
    minimal_r2 = minimal_fe_results[model_name]['R2']
    fe_impact_scores[model_name]['R2_Impact'] = ((full_r2 - minimal_r2) / full_r2) * 100
    
    # MAE Impact
    full_mae = full_fe_results[model_name]['MAE']
    minimal_mae = minimal_fe_results[model_name]['MAE']
    fe_impact_scores[model_name]['MAE_Impact'] = ((minimal_mae - full_mae) / full_mae) * 100
    
    # Accuracy Impact
    full_acc = full_fe_results[model_name]['Accuracy']
    minimal_acc = minimal_fe_results[model_name]['Accuracy']
    fe_impact_scores[model_name]['Accuracy_Impact'] = ((full_acc - minimal_acc) / full_acc) * 100
    
    # F1 Score Impact
    full_f1 = full_fe_results[model_name]['F1_Score']
    minimal_f1 = minimal_fe_results[model_name]['F1_Score']
    fe_impact_scores[model_name]['F1_Impact'] = ((full_f1 - minimal_f1) / full_f1) * 100

    print(f"\n{model_name}:")
    print(f"  RMSE Impact: {fe_impact_scores[model_name]['RMSE_Impact']:+.2f}%")
    print(f"  R² Impact: {fe_impact_scores[model_name]['R2_Impact']:+.2f}%")
    print(f"  MAE Impact: {fe_impact_scores[model_name]['MAE_Impact']:+.2f}%")
    print(f"  Accuracy Impact: {fe_impact_scores[model_name]['Accuracy_Impact']:+.2f}%")
    print(f"  F1 Impact: {fe_impact_scores[model_name]['F1_Impact']:+.2f}%")

# ============================================================================
# STEP 4: GENERATE COMPARISON TABLE
# ============================================================================

print("\n" + "=" * 80)
print("PERFORMANCE COMPARISON TABLE")
print("=" * 80)

comparison_data = []
for model_name in full_fe_results:
    for metric in ['RMSE', 'R2', 'MAE', 'Accuracy', 'F1_Score']:
        comparison_data.append({
            'Model': model_name,
            'Metric': metric,
            'Full FE': full_fe_results[model_name][metric],
            'Minimal FE': minimal_fe_results[model_name][metric],
            'Impact Score': fe_impact_scores[model_name][f'{metric}_Impact']
        })

df_comparison = pd.DataFrame(comparison_data)
print("\n", df_comparison.to_string(index=False))

# ============================================================================
# STEP 5: DETERMINE MODEL RANKINGS
# ============================================================================

print("\n" + "=" * 80)
print("MODEL RANKINGS")
print("=" * 80)

# Rank by RMSE (lower is better)
full_fe_ranking_rmse = sorted(full_fe_results.items(), key=lambda x: x[1]['RMSE'])
minimal_fe_ranking_rmse = sorted(minimal_fe_results.items(), key=lambda x: x[1]['RMSE'])

print("\nRegression Performance (by RMSE):")
print("\nFull FE Dataset:")
for rank, (model, metrics) in enumerate(full_fe_ranking_rmse, 1):
    print(f"  {rank}. {model}: RMSE = {metrics['RMSE']:.2f}")

print("\nMinimal FE Dataset:")
for rank, (model, metrics) in enumerate(minimal_fe_ranking_rmse, 1):
    print(f"  {rank}. {model}: RMSE = {metrics['RMSE']:.2f}")

# Check if ranking changed
ranking_changed = [m[0] for m in full_fe_ranking_rmse] != [m[0] for m in minimal_fe_ranking_rmse]
if ranking_changed:
    print("\n⚠️  MODEL RANKING CHANGED!")
else:
    print("\n✓ Model ranking remained the same")

# ============================================================================
# STEP 6: HYPOTHESIS TESTING
# ============================================================================

print("\n" + "=" * 80)
print("HYPOTHESIS TESTING")
print("=" * 80)

print("\nHypothesis: Feature Engineering disproportionately benefits Linear Regression")

# Calculate average impact scores across all metrics
avg_impact = {}
for model_name in fe_impact_scores:
    avg_impact[model_name] = np.mean([
        abs(fe_impact_scores[model_name]['RMSE_Impact']),
        abs(fe_impact_scores[model_name]['R2_Impact']),
        abs(fe_impact_scores[model_name]['MAE_Impact']),
        abs(fe_impact_scores[model_name]['Accuracy_Impact']),
        abs(fe_impact_scores[model_name]['F1_Impact'])
    ])
    print(f"\n{model_name}: Average Impact = {avg_impact[model_name]:.2f}%")

# Determine most impacted model
most_impacted = max(avg_impact.items(), key=lambda x: x[1])
print(f"\n🎯 Most Impacted by FE Removal: {most_impacted[0]} ({most_impacted[1]:.2f}%)")

# Test hypothesis
if most_impacted[0] == 'Linear Regression':
    print("\n✓ HYPOTHESIS CONFIRMED!")
    print("  Linear Regression is most dependent on feature engineering.")
    print("  Tree-based models are more robust without engineered features.")
else:
    print("\n✗ HYPOTHESIS NOT CONFIRMED")
    print(f"  {most_impacted[0]} showed the highest dependence on feature engineering.")

# ============================================================================
# STEP 7: GENERATE MARKDOWN REPORT
# ============================================================================

print("\n" + "=" * 80)
print("GENERATING REPORT")
print("=" * 80)

report_lines = []
report_lines.append("# Feature Engineering Impact Analysis Report")
report_lines.append("")
report_lines.append(f"**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("")

report_lines.append("## Executive Summary")
report_lines.append("")
report_lines.append(f"This report compares model performance between Full Feature Engineering (209 features) ")
report_lines.append(f"and Minimal Feature Engineering (199 features) datasets to measure the impact of 10 ")
report_lines.append(f"engineered features on model performance.")
report_lines.append("")

report_lines.append("## Performance Comparison")
report_lines.append("")
report_lines.append("### Regression Performance (RMSE)")
report_lines.append("")
report_lines.append("| Model | Full FE | Minimal FE | Change | Impact Score |")
report_lines.append("|-------|---------|------------|--------|--------------|")
for model in full_fe_results:
    full = full_fe_results[model]['RMSE']
    minimal = minimal_fe_results[model]['RMSE']
    change = minimal - full
    impact = fe_impact_scores[model]['RMSE_Impact']
    report_lines.append(f"| {model} | {full:.2f} | {minimal:.2f} | {change:+.2f} | {impact:+.2f}% |")

report_lines.append("")
report_lines.append("### Regression Performance (R² Score)")
report_lines.append("")
report_lines.append("| Model | Full FE | Minimal FE | Change | Impact Score |")
report_lines.append("|-------|---------|------------|--------|--------------|")
for model in full_fe_results:
    full = full_fe_results[model]['R2']
    minimal = minimal_fe_results[model]['R2']
    change = minimal - full
    impact = fe_impact_scores[model]['R2_Impact']
    report_lines.append(f"| {model} | {full:.4f} | {minimal:.4f} | {change:+.4f} | {impact:+.2f}% |")

report_lines.append("")
report_lines.append("### Classification Performance (Accuracy)")
report_lines.append("")
report_lines.append("| Model | Full FE | Minimal FE | Change | Impact Score |")
report_lines.append("|-------|---------|------------|--------|--------------|")
for model in full_fe_results:
    full = full_fe_results[model]['Accuracy']
    minimal = minimal_fe_results[model]['Accuracy']
    change = minimal - full
    impact = fe_impact_scores[model]['Accuracy_Impact']
    report_lines.append(f"| {model} | {full:.4f} | {minimal:.4f} | {change:+.4f} | {impact:+.2f}% |")

report_lines.append("")
report_lines.append("## Model Rankings")
report_lines.append("")
report_lines.append("### Full FE Dataset (by RMSE)")
report_lines.append("")
for rank, (model, metrics) in enumerate(full_fe_ranking_rmse, 1):
    report_lines.append(f"{rank}. **{model}**: {metrics['RMSE']:.2f}")

report_lines.append("")
report_lines.append("### Minimal FE Dataset (by RMSE)")
report_lines.append("")
for rank, (model, metrics) in enumerate(minimal_fe_ranking_rmse, 1):
    report_lines.append(f"{rank}. **{model}**: {metrics['RMSE']:.2f}")

report_lines.append("")
if ranking_changed:
    report_lines.append("**⚠️ Model ranking CHANGED between datasets**")
else:
    report_lines.append("**Model ranking remained consistent**")

report_lines.append("")
report_lines.append("## Feature Engineering Impact Scores")
report_lines.append("")
report_lines.append("Average absolute impact across all metrics:")
report_lines.append("")
for model in sorted(avg_impact.items(), key=lambda x: x[1], reverse=True):
    report_lines.append(f"- **{model[0]}**: {model[1]:.2f}%")

report_lines.append("")
report_lines.append("## Conclusion")
report_lines.append("")
if most_impacted[0] == 'Linear Regression':
    report_lines.append("**Hypothesis CONFIRMED:** Linear Regression is most dependent on feature engineering.")
    report_lines.append("")
    report_lines.append("Key findings:")
    report_lines.append("- Linear Regression showed the largest performance drop without engineered features")
    report_lines.append("- Tree-based models (Random Forest, XGBoost) are more robust without feature engineering")
    report_lines.append("- Engineered features provide explicit patterns that Linear models cannot discover automatically")
    report_lines.append("")
    report_lines.append("**Implications:**")
    report_lines.append("- Use full feature engineering for Linear Regression in production")
    report_lines.append("- Consider minimal feature engineering for tree-based models to reduce complexity")
    report_lines.append("- Tree-based models can automatically discover patterns from raw features")
else:
    report_lines.append(f"**Hypothesis NOT CONFIRMED:** {most_impacted[0]} showed highest dependence on FE.")
    report_lines.append("")
    report_lines.append("This suggests that feature engineering benefits all models, not just linear models.")

report_lines.append("")
report_lines.append("---")
report_lines.append(f"*Generated on {pd.Timestamp.now().strftime('%Y-%m-%d at %H:%M:%S')}*")

# Save report
with open('FE_IMPACT_ANALYSIS.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print("\n✓ Saved: FE_IMPACT_ANALYSIS.md")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
