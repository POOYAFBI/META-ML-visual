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


@lru_cache(maxsize=1)
def _preset_config() -> dict[str, Any]:
    with PRESETS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["presets"]


def _key(task: str, dataset: str) -> str:
    return f"{task.lower()}:{_norm_dataset(dataset)}"


def list_presets(task: str, dataset: str) -> list[dict[str, str]]:
    return [
        {"id": p["id"], "label": p["label"], "description": p.get("description", "")}
        for p in _preset_config().get(_key(task, dataset), [])
    ]


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
        samples.append({
            "id": str(row_index),
            "label": f"نمونه #{display_index}",
            "target": coerce_value(row[target]),
            "features": features,
        })
    return samples


def sample_features(task: str, dataset: str, model_name: str, sample_id: str) -> dict[str, float]:
    for sample in list_samples(task, dataset, model_name, limit=25):
        if sample["id"] == str(sample_id):
            return sample["features"]
    raise ValueError(f"Unknown sample '{sample_id}' for task={task}, dataset={dataset}")
