"""
MODEL LOADING TEST SCRIPT
=========================
Purpose: Verify all 12 saved models can be loaded and used for inference
"""

import joblib
import json
import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 80)
print("MODEL LOADING TEST")
print("=" * 80)
print()

# Load model registry
registry_path = Path("models/model_registry.json")
with open(registry_path, 'r') as f:
    registry = json.load(f)

print(f"Found {len(registry['models'])} models in registry")
print(f"Registry timestamp: {registry['timestamp']}")
print()

# Test each model
successful_loads = 0
failed_loads = 0

for idx, model_info in enumerate(registry['models'], 1):
    task = model_info['task_type']
    dataset = model_info['dataset_type']
    model_name = model_info['model_name']
    model_path = model_info['model_path']
    
    print(f"[{idx}/12] Testing: {task}/{dataset}/{model_name}")
    print(f"        Path: {model_path}")
    
    try:
        # Load the model
        model = joblib.load(model_path)
        print(f"        ✓ Model loaded successfully")
        print(f"        ✓ Model type: {type(model).__name__}")
        
        # Load feature names
        feature_path = model_info['feature_names_path']
        with open(feature_path, 'r') as f:
            feature_info = json.load(f)
            num_features = len(feature_info['feature_names'])
            print(f"        ✓ Features: {num_features}")
        
        # Check if scaler exists
        if model_info['scaler_path']:
            scaler = joblib.load(model_info['scaler_path'])
            print(f"        ✓ Scaler loaded: {type(scaler).__name__}")
        
        # Test prediction on dummy data
        X_dummy = np.random.randn(5, num_features)
        predictions = model.predict(X_dummy)
        print(f"        ✓ Predictions work: {predictions.shape}")
        
        successful_loads += 1
        print(f"        STATUS: ✅ PASSED")
        
    except Exception as e:
        print(f"        ✗ ERROR: {e}")
        failed_loads += 1
        print(f"        STATUS: ❌ FAILED")
    
    print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Models: {len(registry['models'])}")
print(f"Successful Loads: {successful_loads}")
print(f"Failed Loads: {failed_loads}")
print()

if failed_loads == 0:
    print("✅ ALL MODELS PASSED LOADING TEST")
    print("Models are ready for production deployment!")
else:
    print(f"⚠️  WARNING: {failed_loads} model(s) failed to load")
    print("Review error messages above")

print()
print("=" * 80)
