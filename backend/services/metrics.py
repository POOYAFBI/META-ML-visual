from __future__ import annotations

import csv
from functools import lru_cache
from typing import Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
)
from sklearn.model_selection import train_test_split
from .model_loader import load_bundle
from .feature_metadata import feature_meta

CLASS_LABELS_FA = {0: "ارزان", 1: "متوسط", 2: "گران"}


def _class_key(value: Any) -> str:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def _json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _display_label(value: Any) -> str:
    normalized = _json_value(value)
    if isinstance(normalized, int):
        return CLASS_LABELS_FA.get(normalized, f"کلاس {normalized}")
    return f"کلاس {normalized}"


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
        weighted_f1 = float(f1_score(y_test, y_pred, average="weighted"))
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1": weighted_f1,
            "weighted_f1": weighted_f1,
            "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        }

    result = {"metrics": metrics, "actual": y_test.tolist(), "predicted": y_pred.tolist(), "errors": errors.tolist()}
    if task == "regression":
        result.update({
            "error_definition": "predicted - actual",
            "error_unit": "USD",
            "ideal_line_description": "نقطه‌های روی خط ایده‌آل یعنی قیمت پیش‌بینی‌شده دقیقاً برابر قیمت واقعی است.",
        })
    if task == "classification":
        model_classes = getattr(bundle["model"], "classes_", None)
        if model_classes is not None:
            labels = list(model_classes)
        else:
            labels = sorted(np.unique(np.concatenate([y_test, y_pred])).tolist())

        label_keys = [_class_key(cls) for cls in labels]
        display_labels = {key: _display_label(cls) for key, cls in zip(label_keys, labels)}
        class_labels = dict(display_labels)
        matrix = confusion_matrix(y_test, y_pred, labels=labels)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_pred, labels=labels, zero_division=0
        )
        classwise_metrics = {
            key: {
                "label": display_labels[key],
                "precision": float(p),
                "recall": float(r),
                "f1": float(f),
                "support": int(s),
            }
            for key, p, r, f, s in zip(label_keys, precision, recall, f1, support)
        }

        prediction_confidence: list[float] = []
        class_probabilities: list[dict[str, float]] = []
        confident_mistakes: list[dict[str, Any]] = []
        if hasattr(bundle["model"], "predict_proba"):
            proba = bundle["model"].predict_proba(X_model)
            proba_classes = getattr(bundle["model"], "classes_", labels)
            proba_keys = [_class_key(cls) for cls in proba_classes]
            prediction_confidence = [float(value) for value in np.max(proba, axis=1)]
            class_probabilities = [
                {key: float(probability) for key, probability in zip(proba_keys, row)}
                for row in proba
            ]
            confident_mistakes = sorted(
                [
                    {
                        "index": int(index),
                        "actual": _json_value(actual),
                        "predicted": _json_value(predicted),
                        "actual_label": display_labels.get(_class_key(actual), _display_label(actual)),
                        "predicted_label": display_labels.get(_class_key(predicted), _display_label(predicted)),
                        "confidence": prediction_confidence[index],
                        "probabilities": class_probabilities[index],
                    }
                    for index, (actual, predicted) in enumerate(zip(y_test, y_pred))
                    if actual != predicted
                ],
                key=lambda item: item["confidence"],
                reverse=True,
            )[:10]

        result.update({
            "is_correct": (y_pred == y_test).tolist(),
            "actual_class": [_json_value(value) for value in y_test.tolist()],
            "predicted_class": [_json_value(value) for value in y_pred.tolist()],
            "class_labels": class_labels,
            "confusion_matrix": {
                "labels": label_keys,
                "display_labels": display_labels,
                "matrix": matrix.astype(int).tolist(),
            },
            "classwise_metrics": classwise_metrics,
            "prediction_confidence": prediction_confidence,
            "class_probabilities": class_probabilities,
            "confident_mistakes": confident_mistakes,
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
