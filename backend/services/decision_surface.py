from __future__ import annotations

import csv
from typing import Any

import numpy as np

from .metrics import CLASS_LABELS_FA, _class_key, _display_label, _json_value, _num
from .model_loader import load_bundle


def _load_feature_matrix(bundle: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    features = bundle["features"]
    X: list[list[float]] = []
    y: list[float] = []
    with bundle["data_path"].open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            X.append([_num(row.get(feature, "0")) for feature in features])
            y.append(_num(row["price_class"]))
    return np.asarray(X, dtype=float), np.asarray(y)


def _baseline_vector(X: np.ndarray) -> np.ndarray:
    return np.nanmedian(X, axis=0)


def _feature_range(values: np.ndarray) -> tuple[float, float]:
    low, high = np.nanpercentile(values, [2, 98])
    if not np.isfinite(low) or not np.isfinite(high):
        raise ValueError("Unable to compute feature range for selected features.")
    if low == high:
        pad = max(abs(float(low)) * 0.05, 1.0)
        low -= pad
        high += pad
    return float(low), float(high)


def _validate_grid_size(grid_size: int) -> int:
    try:
        size = int(grid_size)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid grid size: grid_size must be an integer between 2 and 80") from exc
    if size < 2 or size > 80:
        raise ValueError("invalid grid size: grid_size must be between 2 and 80")
    return size


def decision_surface(task: str, dataset: str, model_name: str, x_feature: str, y_feature: str, grid_size: int = 40) -> dict[str, Any]:
    if task.lower() != "classification":
        raise ValueError("unsupported task: decision surface is only available for classification")
    size = _validate_grid_size(grid_size)
    bundle = load_bundle(task, dataset, model_name)
    features = bundle["features"]
    missing = [feature for feature in (x_feature, y_feature) if feature not in features]
    if missing:
        raise ValueError(f"unknown feature: {', '.join(missing)}")

    X, y = _load_feature_matrix(bundle)
    x_idx, y_idx = features.index(x_feature), features.index(y_feature)
    x_min, x_max = _feature_range(X[:, x_idx])
    y_min, y_max = _feature_range(X[:, y_idx])
    x_values = np.linspace(x_min, x_max, size)
    y_values = np.linspace(y_min, y_max, size)

    baseline = _baseline_vector(X)
    grid_matrix = np.tile(baseline, (size * size, 1))
    grid_points: list[dict[str, Any]] = []
    row_index = 0
    for y_value in y_values:
        for x_value in x_values:
            grid_matrix[row_index, x_idx] = x_value
            grid_matrix[row_index, y_idx] = y_value
            grid_points.append({"x": float(x_value), "y": float(y_value)})
            row_index += 1

    X_model = bundle["scaler"].transform(grid_matrix) if bundle["scaler"] is not None else grid_matrix
    predictions = bundle["model"].predict(X_model)
    confidences: list[float | None]
    if hasattr(bundle["model"], "predict_proba"):
        proba = bundle["model"].predict_proba(X_model)
        confidences = [float(value) for value in np.max(proba, axis=1)]
    else:
        confidences = [None] * len(grid_points)

    for point, predicted, confidence in zip(grid_points, predictions, confidences):
        point["predicted_class"] = _json_value(predicted)
        if confidence is not None:
            point["confidence"] = confidence

    X_overlay_model = bundle["scaler"].transform(X) if bundle["scaler"] is not None else X
    overlay_pred = bundle["model"].predict(X_overlay_model)
    limit = min(400, len(X))
    if len(X) > limit:
        indices = np.linspace(0, len(X) - 1, limit, dtype=int)
    else:
        indices = np.arange(len(X))
    points = [
        {
            "x": float(X[i, x_idx]),
            "y": float(X[i, y_idx]),
            "actual": _json_value(y[i]),
            "predicted": _json_value(overlay_pred[i]),
            "is_correct": bool(y[i] == overlay_pred[i]),
        }
        for i in indices
    ]

    class_values = getattr(bundle["model"], "classes_", np.unique(np.concatenate([y, predictions])))
    class_keys = [_class_key(value) for value in class_values]
    class_labels = {key: CLASS_LABELS_FA.get(int(key), _display_label(value)) if str(key).lstrip("-").isdigit() else _display_label(value) for key, value in zip(class_keys, class_values)}

    return {
        "x_feature": x_feature,
        "y_feature": y_feature,
        "x_range": [x_min, x_max],
        "y_range": [y_min, y_max],
        "grid_size": size,
        "classes": class_keys,
        "class_labels": class_labels,
        "grid": grid_points,
        "points": points,
    }
