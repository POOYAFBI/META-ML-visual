from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import mean_absolute_error

from .metrics import evaluation
from .model_loader import DISPLAY_DATASETS, registry

MODEL_LABELS = {
    "linear_regression": {"fa": "رگرسیون خطی", "en": "Linear Regression"},
    "logistic_regression": {"fa": "رگرسیون لجستیک", "en": "Logistic Regression"},
    "random_forest": {"fa": "جنگل تصادفی", "en": "Random Forest"},
    "xgboost": {"fa": "ایکس‌جی‌بوست", "en": "XGBoost"},
}

REGRESSION_METRIC_DEFINITIONS = {
    "rmse": {"label": "RMSE", "direction": "lower", "helper_text": "RMSE: lower is better"},
    "mae": {"label": "MAE", "direction": "lower", "helper_text": "MAE: lower is better"},
    "r2": {"label": "R²", "direction": "higher", "helper_text": "R²: higher is better"},
    "normalized_rmse": {"label": "Normalized RMSE", "direction": "lower", "helper_text": "normalized RMSE: lower is better"},
}

CLASSIFICATION_METRIC_DEFINITIONS = {
    "accuracy": {"label": "Accuracy", "direction": "higher", "helper_text": "Accuracy: higher is better"},
    "weighted_f1": {"label": "Weighted F1", "direction": "higher", "helper_text": "Weighted F1: higher is better"},
    "macro_f1": {"label": "Macro F1", "direction": "higher", "helper_text": "Macro F1: higher is better"},
}


def comparison(task: str) -> dict[str, Any]:
    task = task.lower()
    if task not in {"regression", "classification"}:
        raise ValueError("task must be either 'regression' or 'classification'")

    rows = _ranked_rows(task)
    if not rows:
        raise ValueError(f"No registered models found for task={task}")

    best = rows[0]
    primary_metric = "rmse" if task == "regression" else "weighted_f1"
    primary_direction = "lower" if task == "regression" else "higher"
    return {
        "task": task,
        "primary_metric": primary_metric,
        "primary_metric_direction": primary_direction,
        "rows": rows,
        "summary_cards": _summary_cards(task, best, primary_metric, primary_direction),
        "best": {"row_id": best["id"], "rank": best["rank"], "primary_metric_value": best[primary_metric]},
        "insights": _insights(task, best),
        "metric_definitions": REGRESSION_METRIC_DEFINITIONS if task == "regression" else CLASSIFICATION_METRIC_DEFINITIONS,
        "chart_config": _chart_config(task),
    }


def _ranked_rows(task: str) -> list[dict[str, Any]]:
    rows = [_row_for_model(item) for item in registry()["models"] if item["task_type"] == task]
    key = "rmse" if task == "regression" else "weighted_f1"
    reverse = task == "classification"
    rows.sort(key=lambda row: row[key], reverse=reverse)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
        row["interpretation"] = _interpretation(task, row, rank)
    return rows


def _row_for_model(item: dict[str, Any]) -> dict[str, Any]:
    task = item["task_type"]
    dataset_type = item["dataset_type"]
    model_name = item["model_name"]
    dataset_display = _dataset_display(task, dataset_type)
    model_display = MODEL_LABELS.get(model_name, {"fa": model_name.replace("_", " "), "en": model_name.replace("_", " ").title()})
    ev = evaluation(task, dataset_type, model_name)
    row = {
        "id": f"{task[:3]}-{dataset_display['id'].lower()}-{model_name.replace('_', '-')}",
        "dataset_id": dataset_display["id"],
        "dataset_label_fa": dataset_display["labelFa"],
        "dataset_label_en": dataset_display["labelEn"],
        "dataset_raw_name": dataset_type,
        "model_label_fa": model_display["fa"],
        "model_label_en": model_display["en"],
        "model_raw_name": model_name,
    }
    if task == "regression":
        actual = np.asarray(ev["actual"], dtype=float)
        predicted = np.asarray(ev["predicted"], dtype=float)
        rmse = float(ev["metrics"]["rmse"])
        row.update({
            "rmse": rmse,
            "mae": float(mean_absolute_error(actual, predicted)),
            "r2": float(ev["metrics"]["r2"]),
            "normalized_rmse": float(rmse / max(abs(float(np.mean(actual))), 1.0)),
        })
    else:
        metrics = ev["metrics"]
        row.update({
            "accuracy": float(metrics["accuracy"]),
            "weighted_f1": float(metrics.get("weighted_f1", metrics["f1"])),
            "macro_f1": float(metrics["macro_f1"]),
        })
    return row


def _dataset_display(task: str, dataset_type: str) -> dict[str, Any]:
    for item in DISPLAY_DATASETS[task]:
        if item["dataset_type"] == dataset_type:
            return item
    return {"id": dataset_type, "labelFa": dataset_type, "labelEn": dataset_type}


def _summary_cards(task: str, best: dict[str, Any], primary_metric: str, primary_direction: str) -> list[dict[str, str]]:
    best_pair = f"{best['dataset_label_fa']} ({best['dataset_label_en']}) / {best['model_label_fa']} ({best['model_label_en']})"
    return [
        {"id": "best_model", "title": "Best model", "value": f"{best['model_label_fa']} ({best['model_label_en']})", "detail": best["model_raw_name"]},
        {"id": "best_pair", "title": "Best dataset/model pair", "value": best_pair, "detail": f"{best['dataset_raw_name']} / {best['model_raw_name']}"},
        {"id": "primary_metric", "title": "Primary metric", "value": REGRESSION_METRIC_DEFINITIONS.get(primary_metric, CLASSIFICATION_METRIC_DEFINITIONS.get(primary_metric))["label"], "detail": f"{primary_direction} is better"},
        {"id": "key_takeaway", "title": "Key takeaway", "value": _key_takeaway(task, best), "detail": "Computed from registered models and evaluation split"},
    ]


def _insights(task: str, best: dict[str, Any]) -> dict[str, str]:
    if task == "regression":
        return {
            "overall_takeaway": f"بهترین RMSE فعلی متعلق به {best['model_label_fa']} روی {best['dataset_label_fa']} است.",
            "dataset_effect": "اثر دیتاست را با RMSE نرمال‌شده بخوانید تا مقیاس قیمت بین مدل‌ها مقایسه‌پذیرتر شود.",
            "model_behavior": "مدل‌های درختی معمولاً روابط غیرخطی قیمت را بهتر می‌گیرند؛ مدل خطی خط مبنای قابل توضیح‌تری می‌دهد.",
            "metric_caution": "RMSE به خطاهای بزرگ حساس است؛ MAE و R² را همزمان برای تصمیم نهایی بررسی کنید.",
        }
    return {
        "overall_takeaway": f"بهترین Weighted F1 فعلی متعلق به {best['model_label_fa']} روی {best['dataset_label_fa']} است.",
        "dataset_effect": "ویژگی‌سازی را با Weighted F1 و Macro F1 کنار هم بسنجید تا اثر کلاس‌های کم‌تعداد پنهان نشود.",
        "model_behavior": "مدل‌های غیرخطی می‌توانند مرزهای تصمیم پیچیده‌تر را پوشش دهند؛ Logistic Regression خط مبنای ساده‌تری است.",
        "metric_caution": "Accuracy در کلاس‌های نامتوازن کافی نیست؛ Weighted F1 و Macro F1 را کنار آن بخوانید.",
    }


def _chart_config(task: str) -> list[dict[str, str]]:
    if task == "regression":
        return [
            {"id": "rmse_by_pair", "title": "RMSE by model/dataset", "metric": "rmse"},
            {"id": "r2_by_pair", "title": "R² by model/dataset", "metric": "r2"},
        ]
    return [
        {"id": "accuracy_by_pair", "title": "Accuracy by model/dataset", "metric": "accuracy"},
        {"id": "weighted_f1_by_pair", "title": "Weighted F1 by model/dataset", "metric": "weighted_f1"},
    ]


def _interpretation(task: str, row: dict[str, Any], rank: int) -> str:
    if task == "regression":
        if rank == 1:
            return "بهترین خطای RMSE را در ارزیابی فعلی دارد و گزینه اول مقایسه رگرسیون است."
        if row["r2"] >= 0.85:
            return "قدرت توضیح خوبی دارد اما RMSE آن از مدل رتبه اول بیشتر است."
        return "خط مبنای قابل بررسی است اما نسبت به گزینه‌های بالاتر خطای بیشتری نشان می‌دهد."
    if rank == 1:
        return "بهترین Weighted F1 را در ارزیابی فعلی دارد و تعادل کلی کلاس‌ها بهتر است."
    if row["macro_f1"] < row["weighted_f1"] - 0.05:
        return "عملکرد کلی مناسب است اما برای کلاس‌های کوچک‌تر افت Macro F1 دیده می‌شود."
    return "گزینه قابل مقایسه‌ای است اما Weighted F1 آن از مدل رتبه اول کمتر است."


def _key_takeaway(task: str, best: dict[str, Any]) -> str:
    if task == "regression":
        return f"{best['model_label_fa']} کمترین RMSE را با مقدار {best['rmse']:.0f} ثبت کرده است."
    return f"{best['model_label_fa']} بیشترین Weighted F1 را با مقدار {best['weighted_f1']:.3f} ثبت کرده است."
