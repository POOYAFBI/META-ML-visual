from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .model_loader import _norm_dataset, load_bundle
from .predictor import coerce_value

ROOT = Path(__file__).resolve().parents[2]
PRESETS_PATH = ROOT / "backend" / "config" / "presets.json"
KEY_FEATURES = ["GrLivArea", "OverallQual", "YearBuilt"]

FEATURE_LABELS_FA = {
    "GrLivArea": "زیربنا",
    "OverallQual": "کیفیت کلی",
    "YearBuilt": "سال ساخت",
    "Actual SalePrice": "قیمت واقعی",
    "raw_row_id": "شناسه ردیف خام",
}


@lru_cache(maxsize=1)
def _preset_config() -> dict[str, Any]:
    with PRESETS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["presets"]


def _key(task: str, dataset: str) -> str:
    return f"{task.lower()}:{_norm_dataset(dataset)}"


def _active_one_hot(features: dict[str, Any], prefix: str = "Neighborhood_") -> str | None:
    for name, value in features.items():
        if name.startswith(prefix) and coerce_value(value) == 1:
            return name
    return None


def _summary_item(name: str, value: Any, label: str | None = None) -> dict[str, Any]:
    return {"name": name, "label": label or FEATURE_LABELS_FA.get(name, name), "value": value}


def _input_summary(features: dict[str, Any], include_target: Any | None = None, raw_row_id: str | None = None) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    if include_target is not None:
        summary.append(_summary_item("Actual SalePrice", include_target))
    for name in KEY_FEATURES:
        if name in features:
            summary.append(_summary_item(name, coerce_value(features[name])))
    neighborhood = _active_one_hot(features)
    if neighborhood:
        summary.append(_summary_item(neighborhood, neighborhood.removeprefix("Neighborhood_"), "محله فعال"))
    if raw_row_id is not None:
        summary.append(_summary_item("raw_row_id", raw_row_id))
    return summary


def list_presets(task: str, dataset: str) -> list[dict[str, Any]]:
    presets = []
    for p in _preset_config().get(_key(task, dataset), []):
        features = p.get("features", {})
        presets.append({
            "id": p["id"],
            "label": p["label"],
            "description": p.get("description", ""),
            "summary": _input_summary(features),
            "technical_features": features,
        })
    return presets


def preset_features(task: str, dataset: str, model_name: str, preset_id: str) -> dict[str, float]:
    bundle = load_bundle(task, dataset, model_name)
    for preset in _preset_config().get(_key(task, dataset), []):
        if preset["id"] == preset_id:
            source = preset["features"]
            return {name: coerce_value(source.get(name, 0.0)) for name in bundle["features"]}
    raise ValueError(f"Unknown preset '{preset_id}' for task={task}, dataset={dataset}")


def list_samples(task: str, dataset: str, model_name: str, limit: int = 10) -> list[dict[str, Any]]:
    bundle = load_bundle(task, dataset, model_name)
    target = "SalePrice" if task == "regression" else "price_class"
    samples: list[dict[str, Any]] = []
    with bundle["data_path"].open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return samples
    step = max(1, len(rows) // limit)
    for display_index, row_index in enumerate(range(0, len(rows), step), start=1):
        if len(samples) >= limit:
            break
        row = rows[row_index]
        features = {name: coerce_value(row.get(name, 0.0)) for name in bundle["features"]}
        target_value = coerce_value(row[target])
        samples.append({
            "id": str(row_index),
            "label": f"نمونه #{display_index}",
            "target": target_value,
            "raw_row_id": str(row_index),
            "summary": _input_summary(features, include_target=target_value, raw_row_id=str(row_index)),
            "features": features,
        })
    return samples


def sample_features(task: str, dataset: str, model_name: str, sample_id: str) -> dict[str, float]:
    for sample in list_samples(task, dataset, model_name, limit=25):
        if sample["id"] == str(sample_id):
            return sample["features"]
    raise ValueError(f"Unknown sample '{sample_id}' for task={task}, dataset={dataset}")
