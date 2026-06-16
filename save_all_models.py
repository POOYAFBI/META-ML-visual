"""
MODEL PERSISTENCE SCRIPT
========================
Purpose: Train (if needed) and save all 12 machine learning models for production deployment
Author: Automated ML Pipeline
Date: 2026-06-13

This script ensures all trained models are persisted to disk in a structured format
for downstream deployment and inference.

Expected Models:
- 6 Regression models (3 algorithms × 2 datasets)
- 6 Classification models (3 algorithms × 2 datasets)
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor, XGBClassifier

# =============================================================================
# CONFIGURATION
# =============================================================================

MODELS_DIR = Path("models")
RANDOM_STATE = 42

# Define all 12 models to be trained and saved
MODEL_REGISTRY = {
    # REGRESSION MODELS
    'regression': {
        'baseline_dataset': {
            'data_path': 'data/processed_data.csv',
            'models': {
                'linear_regression': {
                    'class': LinearRegression,
                    'params': {},
                    'needs_scaling': False
                },
                'random_forest': {
                    'class': RandomForestRegressor,
                    'params': {'n_estimators': 100, 'random_state': RANDOM_STATE, 'n_jobs': -1},
                    'needs_scaling': False
                },
                'xgboost': {
                    'class': XGBRegressor,
                    'params': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'random_state': RANDOM_STATE},
                    'needs_scaling': False
                }
            }
        },
        'enhanced_dataset': {
            'data_path': 'data/processed_data_minimal_fe.csv',
            'models': {
                'linear_regression': {
                    'class': LinearRegression,
                    'params': {},
                    'needs_scaling': False
                },
                'random_forest': {
                    'class': RandomForestRegressor,
                    'params': {'n_estimators': 100, 'random_state': RANDOM_STATE, 'n_jobs': -1},
                    'needs_scaling': False
                },
                'xgboost': {
                    'class': XGBRegressor,
                    'params': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'random_state': RANDOM_STATE},
                    'needs_scaling': False
                }
            }
        }
    },
    # CLASSIFICATION MODELS
    'classification': {
        'baseline_dataset': {
            'data_path': 'data/processed_data.csv',
            'models': {
                'logistic_regression': {
                    'class': LogisticRegression,
                    'params': {'max_iter': 1000, 'random_state': RANDOM_STATE},
                    'needs_scaling': True
                },
                'random_forest': {
                    'class': RandomForestClassifier,
                    'params': {'n_estimators': 100, 'random_state': RANDOM_STATE, 'n_jobs': -1},
                    'needs_scaling': False
                },
                'xgboost': {
                    'class': XGBClassifier,
                    'params': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.3, 'random_state': RANDOM_STATE, 'eval_metric': 'mlogloss', 'use_label_encoder': False},
                    'needs_scaling': False
                }
            }
        },
        'enhanced_dataset': {
            'data_path': 'data/processed_data_classification_fe.csv',
            'models': {
                'logistic_regression': {
                    'class': LogisticRegression,
                    'params': {'max_iter': 1000, 'random_state': RANDOM_STATE},
                    'needs_scaling': True
                },
                'random_forest': {
                    'class': RandomForestClassifier,
                    'params': {'n_estimators': 100, 'random_state': RANDOM_STATE, 'n_jobs': -1},
                    'needs_scaling': False
                },
                'xgboost': {
                    'class': XGBClassifier,
                    'params': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.3, 'random_state': RANDOM_STATE, 'eval_metric': 'mlogloss', 'use_label_encoder': False},
                    'needs_scaling': False
                }
            }
        }
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_directory_structure():
    """Create the organized directory structure for saving models."""
    print("=" * 80)
    print("CREATING DIRECTORY STRUCTURE")
    print("=" * 80)
    
    dirs_created = []
    
    for task_type in ['regression', 'classification']:
        for dataset_type in ['baseline_dataset', 'enhanced_dataset']:
            dir_path = MODELS_DIR / task_type / dataset_type
            dir_path.mkdir(parents=True, exist_ok=True)
            dirs_created.append(str(dir_path))
            print(f"✓ Created: {dir_path}")
    
    print(f"\n✓ Total directories: {len(dirs_created)}")
    print()
    return dirs_created


def load_and_prepare_data(data_path, task_type):
    """
    Load and prepare data for training.
    
    Args:
        data_path: Path to CSV file
        task_type: 'regression' or 'classification'
    
    Returns:
        X_train, X_test, y_train, y_test, feature_names
    """
    print(f"   Loading data: {data_path}")
    df = pd.read_csv(data_path)
    
    # Determine target column
    if task_type == 'regression':
        target_col = 'SalePrice'
        exclude_cols = ['SalePrice', 'price_class']
    else:  # classification
        target_col = 'price_class'
        exclude_cols = ['SalePrice', 'price_class']
    
    # Separate features and target
    X = df.drop(columns=[col for col in exclude_cols if col in df.columns])
    y = df[target_col]
    
    feature_names = X.columns.tolist()
    
    # Handle missing values
    if X.isnull().sum().sum() > 0:
        print(f"   Handling missing values...")
        X = X.fillna(X.median())
    
    # Train-test split
    if task_type == 'classification':
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE
        )
    
    print(f"   ✓ Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"   ✓ Split: {X_train.shape[0]} train, {X_test.shape[0]} test")
    
    return X_train, X_test, y_train, y_test, feature_names


def train_and_save_model(task_type, dataset_type, model_name, model_config, data_path):
    """
    Train a single model and save it to disk.
    
    Args:
        task_type: 'regression' or 'classification'
        dataset_type: 'baseline_dataset' or 'enhanced_dataset'
        model_name: Name of the model (e.g., 'linear_regression')
        model_config: Configuration dictionary with model class and params
        data_path: Path to the training data
    
    Returns:
        dict with training metadata
    """
    print(f"\n{'='*80}")
    print(f"TRAINING: {task_type.upper()} - {dataset_type.replace('_', ' ').upper()} - {model_name.replace('_', ' ').upper()}")
    print(f"{'='*80}")
    
    # Load and prepare data
    X_train, X_test, y_train, y_test, feature_names = load_and_prepare_data(data_path, task_type)
    
    # Handle scaling if needed
    scaler = None
    if model_config['needs_scaling']:
        print(f"   Applying feature scaling (StandardScaler)...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        X_train_final = X_train_scaled
        X_test_final = X_test_scaled
    else:
        # Convert to numpy arrays
        X_train_final = X_train.values
        X_test_final = X_test.values
    
    # Initialize model
    model_class = model_config['class']
    model_params = model_config['params']
    model = model_class(**model_params)
    
    print(f"   Training {model_class.__name__}...")
    print(f"   Parameters: {model_params}")
    
    # Train model
    model.fit(X_train_final, y_train)
    print(f"   ✓ Training complete")
    
    # Evaluate model
    train_score = model.score(X_train_final, y_train)
    test_score = model.score(X_test_final, y_test)
    
    print(f"   Train Score (R²/Accuracy): {train_score:.4f}")
    print(f"   Test Score (R²/Accuracy):  {test_score:.4f}")
    
    # Determine save path
    save_dir = MODELS_DIR / task_type / dataset_type
    model_filename = f"{model_name}.pkl"
    model_path = save_dir / model_filename
    
    # Save model using joblib (handles sklearn and xgboost)
    print(f"   Saving model to: {model_path}")
    joblib.dump(model, model_path)
    
    # Save scaler if used
    scaler_path = None
    if scaler is not None:
        scaler_filename = f"{model_name}_scaler.pkl"
        scaler_path = save_dir / scaler_filename
        print(f"   Saving scaler to: {scaler_path}")
        joblib.dump(scaler, scaler_path)
    
    # Save feature names
    feature_names_path = save_dir / f"{model_name}_features.json"
    with open(feature_names_path, 'w') as f:
        json.dump({'feature_names': feature_names}, f, indent=2)
    
    print(f"   ✓ Model saved successfully")
    
    # Return metadata
    metadata = {
        'task_type': task_type,
        'dataset_type': dataset_type,
        'model_name': model_name,
        'model_class': model_class.__name__,
        'model_path': str(model_path),
        'scaler_path': str(scaler_path) if scaler_path else None,
        'feature_names_path': str(feature_names_path),
        'train_score': float(train_score),
        'test_score': float(test_score),
        'num_features': len(feature_names),
        'train_samples': X_train.shape[0],
        'test_samples': X_test.shape[0],
        'trained_at': datetime.now().isoformat()
    }
    
    return metadata


def verify_model_loadable(model_path):
    """
    Verify that a saved model can be loaded from disk.
    
    Args:
        model_path: Path to the saved model file
    
    Returns:
        bool: True if model loads successfully
    """
    try:
        model = joblib.load(model_path)
        return True
    except Exception as e:
        print(f"   ✗ ERROR loading {model_path}: {e}")
        return False


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    print("=" * 80)
    print("MODEL PERSISTENCE & EXPORT PIPELINE")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Models Expected: 12 (6 regression + 6 classification)")
    print()
    
    # Step 1: Create directory structure
    create_directory_structure()
    
    # Step 2: Train and save all models
    all_metadata = []
    total_models = 0
    successful_saves = 0
    failed_saves = 0
    
    for task_type, task_config in MODEL_REGISTRY.items():
        for dataset_type, dataset_config in task_config.items():
            data_path = dataset_config['data_path']
            
            for model_name, model_config in dataset_config['models'].items():
                total_models += 1
                
                try:
                    metadata = train_and_save_model(
                        task_type=task_type,
                        dataset_type=dataset_type,
                        model_name=model_name,
                        model_config=model_config,
                        data_path=data_path
                    )
                    all_metadata.append(metadata)
                    successful_saves += 1
                    
                except Exception as e:
                    print(f"\n   ✗ ERROR: Failed to train/save {model_name}")
                    print(f"   Error details: {e}")
                    failed_saves += 1
    
    # Step 3: Verify all models are loadable
    print("\n" + "=" * 80)
    print("VERIFYING MODEL PERSISTENCE")
    print("=" * 80)
    
    loadable_count = 0
    for metadata in all_metadata:
        model_path = metadata['model_path']
        is_loadable = verify_model_loadable(model_path)
        
        if is_loadable:
            print(f"✓ {model_path}")
            loadable_count += 1
        else:
            print(f"✗ {model_path}")
    
    print(f"\n✓ Loadable models: {loadable_count}/{len(all_metadata)}")
    
    # Step 4: Save comprehensive metadata
    print("\n" + "=" * 80)
    print("SAVING METADATA")
    print("=" * 80)
    
    metadata_path = MODELS_DIR / "model_registry.json"
    with open(metadata_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_models': total_models,
            'successful_saves': successful_saves,
            'failed_saves': failed_saves,
            'loadable_count': loadable_count,
            'models': all_metadata
        }, f, indent=2)
    
    print(f"✓ Metadata saved to: {metadata_path}")
    
    # Step 5: Generate final report
    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print(f"\nTotal Models: {total_models}")
    print(f"Successfully Saved: {successful_saves}")
    print(f"Failed: {failed_saves}")
    print(f"Verified Loadable: {loadable_count}")
    print()
    
    print("SAVED MODELS BY CATEGORY:")
    print("-" * 80)
    
    # Group by task and dataset
    for task_type in ['regression', 'classification']:
        print(f"\n{task_type.upper()}:")
        for dataset_type in ['baseline_dataset', 'enhanced_dataset']:
            dataset_label = "Baseline Dataset" if dataset_type == 'baseline_dataset' else "Enhanced Dataset"
            print(f"\n  {dataset_label}:")
            
            models_in_category = [m for m in all_metadata 
                                 if m['task_type'] == task_type 
                                 and m['dataset_type'] == dataset_type]
            
            for model_meta in models_in_category:
                print(f"    ✓ {model_meta['model_name']:25s} → {model_meta['model_path']}")
    
    print("\n" + "=" * 80)
    print("MODEL PERSISTENCE COMPLETE")
    print("=" * 80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Return summary for testing
    return {
        'total': total_models,
        'successful': successful_saves,
        'failed': failed_saves,
        'loadable': loadable_count,
        'metadata': all_metadata
    }


if __name__ == "__main__":
    try:
        result = main()
        
        # Exit with appropriate code
        if result['failed'] > 0:
            print(f"\n⚠ WARNING: {result['failed']} model(s) failed to save")
            sys.exit(1)
        elif result['loadable'] < result['successful']:
            print(f"\n⚠ WARNING: Some models are not loadable")
            sys.exit(1)
        else:
            print("\n✓ SUCCESS: All models saved and verified")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
