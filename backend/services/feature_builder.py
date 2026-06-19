from __future__ import annotations

import csv
import math
from functools import lru_cache
from typing import Any

import numpy as np

from .model_loader import load_bundle

TARGET_COLUMNS = {"SalePrice", "price_class"}
CURRENT_YEAR = 2024

ALIASES = {
    "area": "GrLivArea",
    "living_area": "GrLivArea",
    "sqft": "GrLivArea",
    "bedrooms": "BedroomAbvGr",
    "bedroom": "BedroomAbvGr",
    "bathrooms": "TotalBathrooms",
    "bathroom": "TotalBathrooms",
    "full_bathrooms": "FullBath",
    "half_bathrooms": "HalfBath",
    "basement_area": "TotalBsmtSF",
    "garage_area": "GarageArea",
    "garage_cars": "GarageCars",
    "year_built": "YearBuilt",
    "year_remodeled": "YearRemodAdd",
    "overall_quality": "OverallQual",
    "overall_condition": "OverallCond",
    "lot_area": "LotArea",
    "location": "Neighborhood",
    "neighborhood": "Neighborhood",
}


def coerce_feature_value(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    if value is None or value == "":
        return math.nan
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes"}:
            return 1.0
        if lowered in {"false", "no"}:
            return 0.0
    return float(value)


@lru_cache(maxsize=16)
def training_schema(task: str, dataset: str, model_name: str) -> dict[str, Any]:
    bundle = load_bundle(task, dataset, model_name)
    features = list(bundle["features"])
    sums = {name: 0.0 for name in features}
    counts = {name: 0 for name in features}
    rows = 0
    with bundle["data_path"].open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        dataset_columns = list(reader.fieldnames or [])
        for row in reader:
            rows += 1
            for name in features:
                try:
                    value = coerce_feature_value(row.get(name))
                except (TypeError, ValueError):
                    continue
                if math.isfinite(value):
                    sums[name] += value
                    counts[name] += 1
    means = {name: (sums[name] / counts[name] if counts[name] else 0.0) for name in features}
    one_hot_groups: dict[str, list[str]] = {}
    for name in features:
        if "_" in name and not name.endswith("_encoded") and name != "TotalSF_x_OverallQual":
            group, _ = name.split("_", 1)
            one_hot_groups.setdefault(group, []).append(name)
    return {
        "features": features,
        "means": means,
        "one_hot_groups": one_hot_groups,
        "dataset_columns": dataset_columns,
        "row_count": rows,
    }


def _provided(payload: dict[str, Any], *names: str) -> bool:
    return any(name in payload and payload[name] not in (None, "") for name in names)


def _value(values: dict[str, float], name: str) -> float:
    value = values.get(name, 0.0)
    return 0.0 if not math.isfinite(value) else float(value)


def _set_if_present(values: dict[str, float], payload: dict[str, Any], target: str, source: str | None = None) -> bool:
    source = source or target
    if source not in payload or payload[source] in (None, ""):
        return False
    values[target] = coerce_feature_value(payload[source])
    return True


def _apply_aliases(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload or {})
    for alias, target in ALIASES.items():
        if alias in payload and target not in normalized:
            normalized[target] = payload[alias]
    return normalized


def _apply_one_hot(values: dict[str, float], payload: dict[str, Any], groups: dict[str, list[str]]) -> list[str]:
    selected: list[str] = []
    for group, columns in groups.items():
        raw_value = payload.get(group)
        if raw_value in (None, ""):
            continue
        raw_text = str(raw_value).strip()
        match = raw_text if raw_text.startswith(f"{group}_") else f"{group}_{raw_text}"
        for column in columns:
            values[column] = 1.0 if column == match else 0.0
        selected.append(match if match in columns else f"{group}=base_or_unknown:{raw_text}")
    return selected


def _apply_direct_features(values: dict[str, float], payload: dict[str, Any], features: list[str]) -> list[str]:
    applied: list[str] = []
    feature_set = set(features)
    for name, raw in payload.items():
        if name in feature_set and raw not in (None, ""):
            values[name] = coerce_feature_value(raw)
            applied.append(name)
    return applied


def _apply_engineering(values: dict[str, float], payload: dict[str, Any], features: set[str]) -> list[str]:
    engineered: list[str] = []

    def set_feature(name: str, value: float) -> None:
        if name in features and math.isfinite(value):
            values[name] = float(value)
            engineered.append(name)

    if _provided(payload, "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "area", "living_area", "sqft"):
        set_feature("TotalSF", _value(values, "TotalBsmtSF") + _value(values, "1stFlrSF") + _value(values, "2ndFlrSF"))
    if _provided(payload, "YearBuilt", "year_built"):
        set_feature("HouseAge", CURRENT_YEAR - _value(values, "YearBuilt"))
    if _provided(payload, "YearRemodAdd", "year_remodeled"):
        set_feature("YearsSinceRemod", CURRENT_YEAR - _value(values, "YearRemodAdd"))
    if _provided(payload, "FullBath", "HalfBath", "BsmtFullBath", "BsmtHalfBath", "bathrooms", "bathroom"):
        if _provided(payload, "bathrooms", "bathroom") and not _provided(payload, "FullBath", "HalfBath", "BsmtFullBath", "BsmtHalfBath"):
            set_feature("TotalBathrooms", _value(values, "TotalBathrooms"))
        else:
            set_feature("TotalBathrooms", _value(values, "FullBath") + 0.5 * _value(values, "HalfBath") + _value(values, "BsmtFullBath") + 0.5 * _value(values, "BsmtHalfBath"))
    if _provided(payload, "OverallQual", "OverallCond", "overall_quality", "overall_condition"):
        set_feature("OverallScore", _value(values, "OverallQual") * _value(values, "OverallCond"))
    if _provided(payload, "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch"):
        set_feature("TotalPorchSF", _value(values, "OpenPorchSF") + _value(values, "EnclosedPorch") + _value(values, "3SsnPorch") + _value(values, "ScreenPorch"))
    if _provided(payload, "GarageArea", "garage_area"):
        set_feature("HasGarage", 1.0 if _value(values, "GarageArea") > 0 else 0.0)
    if _provided(payload, "TotalBsmtSF", "basement_area"):
        set_feature("HasBasement", 1.0 if _value(values, "TotalBsmtSF") > 0 else 0.0)
    if _provided(payload, "Fireplaces"):
        set_feature("HasFireplace", 1.0 if _value(values, "Fireplaces") > 0 else 0.0)
    if _provided(payload, "YearBuilt", "YearRemodAdd", "year_built", "year_remodeled"):
        set_feature("IsRemodeled", 1.0 if _value(values, "YearBuilt") != _value(values, "YearRemodAdd") else 0.0)
    if _provided(payload, "TotalSF", "OverallQual", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "overall_quality"):
        set_feature("TotalSF_x_OverallQual", _value(values, "TotalSF") * _value(values, "OverallQual"))
        total_sf = max(_value(values, "TotalSF"), 0.0)
        set_feature("TotalSF_log", math.log1p(total_sf))
    if _provided(payload, "LotArea", "lot_area"):
        set_feature("LotArea_log", math.log1p(max(_value(values, "LotArea"), 0.0)))
    return engineered


def build_features(task: str, dataset: str, model_name: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    bundle = load_bundle(task, dataset, model_name)
    schema = training_schema(task, dataset, model_name)
    features = schema["features"]
    payload = _apply_aliases(payload or {})
    values = dict(schema["means"])
    direct = _apply_direct_features(values, payload, features)
    selected = _apply_one_hot(values, payload, schema["one_hot_groups"])
    engineered = _apply_engineering(values, payload, set(features))
    vector = np.asarray([[values[name] for name in features]], dtype=float)
    validation = validate_feature_vector(bundle, vector, features)
    preview = [
        {"feature": name, "value": float(values[name]), "source": "input" if name in direct else "engineered" if name in engineered else "training_mean"}
        for name in features[:25]
    ]
    return {
        "vector": vector,
        "features": features,
        "values": values,
        "validation": validation,
        "preview": preview,
        "applied_inputs": sorted(set(direct)),
        "engineered_features": sorted(set(engineered)),
        "categorical_selections": selected,
        "defaults_used": [name for name in features if name not in set(direct) | set(engineered)],
    }


def validate_feature_vector(bundle: dict[str, Any], vector: np.ndarray, features: list[str]) -> dict[str, Any]:
    expected = int(getattr(bundle["model"], "n_features_in_", len(features)))
    actual = int(vector.shape[1]) if vector.ndim == 2 else 0
    nan_count = int(np.isnan(vector).sum())
    finite = bool(np.isfinite(vector).all())
    ok = actual == expected and nan_count == 0 and finite and len(features) == expected
    errors: list[str] = []
    if actual != expected:
        errors.append(f"feature count mismatch: expected {expected}, got {actual}")
    if len(features) != expected:
        errors.append(f"feature schema mismatch: expected {expected} names, got {len(features)}")
    if nan_count:
        errors.append(f"feature vector contains {nan_count} NaN values")
    if not finite:
        errors.append("feature vector contains non-finite values")
    return {"ok": ok, "expected_features": expected, "actual_features": actual, "nan_count": nan_count, "finite": finite, "errors": errors}
