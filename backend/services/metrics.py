from __future__ import annotations

import csv
from functools import lru_cache
from typing import Any
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from .model_loader import load_bundle
from .feature_metadata import feature_meta

CLASS_LABELS_FA = {0: "ارزان", 1: "متوسط", 2: "گران"}


def _num(v: str) -> float:
    if v in ("", "NA", "NaN"): return 0.0
    if v.lower() == "true": return 1.0
    if v.lower() == "false": return 0.0
    return float(v)


def _load_xy(bundle: dict[str, Any], task: str) -> tuple[np.ndarray, np.ndarray]:
    features = bundle["features"]
    target = "SalePrice" if task == "regression" else "price_class"
    X, y = [], []
    with bundle["data_path"].open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            X.append([_num(row.get(f, "0")) for f in features])
            y.append(_num(row[target]))
    return np.asarray(X, dtype=float), np.asarray(y)


@lru_cache(maxsize=64)
def evaluation(task: str, dataset: str, model_name: str) -> dict[str, Any]:
    bundle = load_bundle(task, dataset, model_name)
    X, y = _load_xy(bundle, task)
    stratify = y if task == "classification" else None
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify)
    X_model = bundle["scaler"].transform(X_test) if bundle["scaler"] is not None else X_test
    y_pred = bundle["model"].predict(X_model)
    if task == "regression":
        errors = y_pred - y_test
        metrics = {"rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))), "r2": float(r2_score(y_test, y_pred))}
    else:
        errors = y_pred - y_test
        metrics = {"accuracy": float(accuracy_score(y_test, y_pred)), "f1": float(f1_score(y_test, y_pred, average="weighted"))}

    result = {"metrics": metrics, "actual": y_test.tolist(), "predicted": y_pred.tolist(), "errors": errors.tolist()}
    if task == "regression":
        result.update({
            "error_definition": "predicted - actual",
            "error_unit": "USD",
            "ideal_line_description": "نقطه‌های روی خط ایده‌آل یعنی قیمت پیش‌بینی‌شده دقیقاً برابر قیمت واقعی است.",
        })
    if task == "classification":
        unique_classes = sorted({int(v) for v in np.concatenate([y_test, y_pred])})
        result.update({
            "is_correct": (y_pred == y_test).tolist(),
            "actual_class": y_test.tolist(),
            "predicted_class": y_pred.tolist(),
            "class_labels": {str(cls): CLASS_LABELS_FA.get(cls, f"کلاس {cls}") for cls in unique_classes},
        })
    return result


@lru_cache(maxsize=64)
def mean_target_value(task: str, dataset: str, model_name: str) -> float:
    bundle = load_bundle(task, dataset, model_name)
    _, y = _load_xy(bundle, task)
    return float(np.mean(y))


def feature_importance(task: str, dataset: str, model_name: str) -> list[dict[str, float | str]]:
    bundle = load_bundle(task, dataset, model_name)
    model = bundle["model"]
    values = getattr(model, "feature_importances_", None)
    if values is None and hasattr(model, "coef_"):
        values = np.abs(np.ravel(model.coef_))
    if values is None:
        return []
    pairs = sorted(zip(bundle["features"], values), key=lambda p: float(p[1]), reverse=True)[:20]
    return [
        {
            "feature": f,
            "importance": float(v),
            "display_name_fa": feature_meta(f)["display_name_fa"],
            "display_name_en": feature_meta(f)["display_name_en"],
            "raw_feature": feature_meta(f)["raw_feature"],
            "feature_group": feature_meta(f)["feature_group"],
        }
        for f, v in pairs
    ]
