from __future__ import annotations

from typing import Any
import numpy as np
from .model_loader import load_bundle
from .metrics import evaluation, mean_target_value
from .feature_builder import build_features


def coerce_value(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    if value is None or value == "":
        return 0.0
    if isinstance(value, str):
        if value.lower() in {"true", "yes"}: return 1.0
        if value.lower() in {"false", "no"}: return 0.0
    return float(value)


def feature_vector(features: list[str], payload: dict[str, Any]) -> np.ndarray:
    return np.array([[coerce_value(payload.get(name, 0.0)) for name in features]], dtype=float)


def _confidence_label(confidence: float, task_type: str) -> tuple[str, str, str]:
    basis = "خطای مدل (RMSE)" if task_type == "regression" else "احتمال کلاس پیش‌بینی‌شده"
    if confidence > 0.8:
        return "high", "High", f"این پیش‌بینی بر اساس {basis}، قابلیت اتکای بالایی دارد."
    if confidence >= 0.5:
        return "medium", "Medium", f"این پیش‌بینی بر اساس {basis}، قابلیت اتکای متوسطی دارد."
    return "low", "Low", f"این پیش‌بینی بر اساس {basis}، قابلیت اتکای پایینی دارد."


def _metadata(bundle: dict[str, Any]) -> dict[str, Any]:
    info = bundle["info"]
    return {
        "model_name": info["model_name"],
        "model_class": info.get("model_class"),
        "task_type": info["task_type"],
        "dataset_used": info["dataset_type"],
    }


def _analysis(confidence: float, task_type: str) -> dict[str, Any]:
    level, label, explanation = _confidence_label(confidence, task_type)
    return {"reliability": level, "label": label, "explanation": explanation}


def predict(task: str, dataset: str, model_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
    bundle = load_bundle(task, dataset, model_name)
    task_type = bundle["info"]["task_type"]
    built = build_features(task, dataset, model_name, inputs)
    validation = built["validation"]
    if not validation["ok"]:
        raise ValueError("Invalid feature vector: " + "; ".join(validation["errors"]))
    X = built["vector"]
    if bundle["scaler"] is not None:
        X = bundle["scaler"].transform(X)

    pred = bundle["model"].predict(X)[0]
    result: dict[str, Any] = {
        "prediction": float(pred) if task_type == "regression" else int(pred),
        "model_metadata": _metadata(bundle),
        "raw_model_output": float(pred) if task_type == "regression" else int(pred),
        "feature_validation": validation,
        "feature_preview": built["preview"],
        "feature_builder": {
            "applied_inputs": built["applied_inputs"],
            "engineered_features": built["engineered_features"],
            "categorical_selections": built["categorical_selections"],
            "defaults_used_count": len(built["defaults_used"]),
        },
    }

    if task_type == "regression":
        rmse = float(evaluation(task_type, dataset, model_name)["metrics"]["rmse"])
        mean_target = float(mean_target_value(task_type, dataset, model_name))
        confidence = 0.0 if mean_target == 0 else 1 - (rmse / mean_target)
        confidence = float(np.clip(confidence, 0.0, 1.0))
        prediction = float(pred)
        result.update({
            "error_estimate": {"metric": "RMSE", "value": rmse, "description": "RMSE میانگین اندازه خطای مدل روی داده آزمون است و با واحد دلار گزارش می‌شود."},
            "prediction_range": {
                "lower": prediction - rmse,
                "upper": prediction + rmse,
                "basis": "بازه از کم و زیاد کردن یک RMSE از مقدار پیش‌بینی ساخته شده است.",
                "metric": "RMSE",
                "metric_value": rmse,
            },
            "confidence": confidence,
            "confidence_basis": "1 - (RMSE / mean target price), clipped to the 0..1 range",
            "confidence_label": "RMSE-based Confidence",
            "confidence_explanation": "این عدد احتمال درست بودن نیست؛ از نسبت RMSE به میانگین قیمت ساخته شده است.",
            "analysis": _analysis(confidence, task_type),
        })
        return result

    probabilities: dict[str, float] = {}
    confidence = 1.0
    if hasattr(bundle["model"], "predict_proba"):
        probs = bundle["model"].predict_proba(X)[0]
        classes = getattr(bundle["model"], "classes_", range(len(probs)))
        probabilities = {str(cls): float(prob) for cls, prob in zip(classes, probs)}
        confidence = float(np.max(probs))

    result.update({
        "predicted_class": int(pred),
        "class_probabilities": probabilities,
        "confidence": confidence,
        "analysis": _analysis(confidence, task_type),
    })
    return result
