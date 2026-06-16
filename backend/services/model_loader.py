from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "models" / "model_registry.json"

MODEL_ALIASES = {
    "linear": "linear_regression",
    "logistic": "logistic_regression",
    "rf": "random_forest",
    "randomforest": "random_forest",
    "xgb": "xgboost",
}

# User-facing A/B/C labels mapped to real trained dataset folders. Dataset C is the
# classification feature-engineered dataset; regression has only A/B trained models.
DATASET_ALIASES = {
    "A": "baseline_dataset",
    "B": "enhanced_dataset",
    "C": "enhanced_dataset",
    "baseline": "baseline_dataset",
    "baseline_dataset": "baseline_dataset",
    "enhanced": "enhanced_dataset",
    "enhanced_dataset": "enhanced_dataset",
}

DATA_PATHS = {
    ("regression", "baseline_dataset"): ROOT / "data" / "processed_data.csv",
    ("regression", "enhanced_dataset"): ROOT / "data" / "processed_data_minimal_fe.csv",
    ("classification", "baseline_dataset"): ROOT / "data" / "processed_data.csv",
    ("classification", "enhanced_dataset"): ROOT / "data" / "processed_data_classification_fe.csv",
}

DISPLAY_DATASETS = {
    "regression": [
        {"id": "A", "name": "دیتاست A — پایه (Dataset A / baseline_dataset)", "dataset_type": "baseline_dataset", "raw": "baseline_dataset", "labelFa": "دیتاست A — پایه", "labelEn": "Dataset A / baseline_dataset", "short": "A"},
        {"id": "B", "name": "دیتاست B — ویژگی‌سازی حداقلی (Dataset B / enhanced_dataset)", "dataset_type": "enhanced_dataset", "raw": "enhanced_dataset", "labelFa": "دیتاست B — ویژگی‌سازی حداقلی", "labelEn": "Dataset B / enhanced_dataset", "short": "B"},
    ],
    "classification": [
        {"id": "A", "name": "دیتاست A — پایه (Dataset A / baseline_dataset)", "dataset_type": "baseline_dataset", "raw": "baseline_dataset", "labelFa": "دیتاست A — پایه", "labelEn": "Dataset A / baseline_dataset", "short": "A"},
        {"id": "C", "name": "دیتاست C — ویژگی‌سازی طبقه‌بندی (Dataset C / enhanced_dataset)", "dataset_type": "enhanced_dataset", "raw": "enhanced_dataset", "labelFa": "دیتاست C — ویژگی‌سازی طبقه‌بندی", "labelEn": "Dataset C / enhanced_dataset", "short": "C"},
    ],
}


def _norm_model(model_name: str) -> str:
    key = model_name.strip().lower().replace("-", "_").replace(" ", "_")
    return MODEL_ALIASES.get(key, key)


def _norm_dataset(dataset: str) -> str:
    key = dataset.strip()
    return DATASET_ALIASES.get(key, DATASET_ALIASES.get(key.upper(), key))


ALLOWED_PATH_ROOTS = (ROOT / "models", ROOT / "data")


def _safe_path_label(path_text: str) -> str:
    return Path(path_text.replace("\\", "/")).name or "requested file"


def _fixed_path(path_text: str | None, *, expected_suffixes: set[str] | None = None) -> Path | None:
    if not path_text:
        return None

    normalized_text = path_text.replace("\\", "/")
    resolved_path = (ROOT / normalized_text).resolve()
    allowed_roots = tuple(path.resolve() for path in ALLOWED_PATH_ROOTS)

    if not any(resolved_path.is_relative_to(allowed_root) for allowed_root in allowed_roots):
        raise ValueError("The requested model file is outside the allowed application storage area.")

    file_label = _safe_path_label(path_text)
    if not resolved_path.is_file():
        raise ValueError(f"The requested model file '{file_label}' is not available.")

    if expected_suffixes and resolved_path.suffix.lower() not in expected_suffixes:
        allowed = ", ".join(sorted(expected_suffixes))
        raise ValueError(f"The requested model file '{file_label}' has an unsupported file type. Expected: {allowed}.")

    return resolved_path


@lru_cache(maxsize=1)
def registry() -> dict[str, Any]:
    with REGISTRY_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def available_options() -> dict[str, Any]:
    out: dict[str, Any] = {"tasks": {}}
    for task in ("regression", "classification"):
        models = sorted({m["model_name"] for m in registry()["models"] if m["task_type"] == task})
        out["tasks"][task] = {"datasets": DISPLAY_DATASETS[task], "models": models}
    return out


def model_info(task: str, dataset: str, model_name: str) -> dict[str, Any]:
    task = task.lower()
    ds = _norm_dataset(dataset)
    name = _norm_model(model_name)
    for item in registry()["models"]:
        if item["task_type"] == task and item["dataset_type"] == ds and item["model_name"] == name:
            return item
    raise ValueError(f"No trained model found for task={task}, dataset={dataset}, model={model_name}")


@lru_cache(maxsize=64)
def load_bundle(task: str, dataset: str, model_name: str) -> dict[str, Any]:
    info = model_info(task, dataset, model_name)
    feature_names_path = _fixed_path(info["feature_names_path"], expected_suffixes={".json"})
    with feature_names_path.open(encoding="utf-8") as fh:
        features = json.load(fh)["feature_names"]
    model_path = _fixed_path(info["model_path"], expected_suffixes={".pkl"})
    scaler_path = _fixed_path(info.get("scaler_path"), expected_suffixes={".pkl"})
    return {
        "info": info,
        "model": joblib.load(model_path),
        "scaler": joblib.load(scaler_path) if scaler_path else None,
        "features": features,
        "data_path": DATA_PATHS[(info["task_type"], info["dataset_type"])],
    }
