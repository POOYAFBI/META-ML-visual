from __future__ import annotations

from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .services.model_loader import available_options, load_bundle
from .services.predictor import predict
from .services.metrics import evaluation, feature_importance
from .services.inputs import list_presets, list_samples, preset_features, sample_features

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Persian ML Housing App")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PredictRequest(BaseModel):
    task: str
    dataset: str
    model: str
    features: dict[str, Any] = Field(default_factory=dict)
    input_mode: str = "advanced"
    preset_id: str | None = None
    sample_id: str | None = None

@app.get("/api/options")
def options():
    return available_options()

FEATURE_FA = {
    "OverallQual": "کیفیت کلی ساختمان",
    "OverallCond": "وضعیت کلی ساختمان",
    "GrLivArea": "زیربنای قابل سکونت",
    "YearBuilt": "سال ساخت",
    "YearRemodAdd": "سال بازسازی",
    "LotArea": "مساحت زمین",
    "TotalBsmtSF": "مساحت زیرزمین",
    "TotalSF": "مساحت کل",
    "GarageArea": "مساحت پارکینگ",
    "GarageCars": "ظرفیت پارکینگ",
    "FullBath": "حمام کامل",
    "BedroomAbvGr": "تعداد اتاق خواب",
    "TotRmsAbvGrd": "تعداد اتاق‌ها",
    "Fireplaces": "تعداد شومینه",
    "Neighborhood": "محله",
}
AREA_FEATURES = {"GrLivArea", "LotArea", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GarageArea", "WoodDeckSF", "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch", "PoolArea", "TotalSF", "TotalPorchSF"}
GENERAL_FEATURES = {"MSSubClass", "YearBuilt", "YearRemodAdd", "HouseAge", "YearsSinceRemod", "MoSold", "YrSold"}
QUALITY_FEATURES = {"OverallQual", "OverallCond", "OverallScore"}
AMENITY_FEATURES = {"FullBath", "HalfBath", "BedroomAbvGr", "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "GarageCars", "TotalBathrooms", "HasGarage", "HasBasement", "HasFireplace", "IsRemodeled"}

def _feature_meta(name: str) -> dict[str, Any]:
    raw_name = name
    one_hot = "_" in name and name not in {"TotalSF_x_OverallQual"}
    prefix, value = name.split("_", 1) if one_hot else (name, "")
    if prefix == "Neighborhood":
        group, label_fa, input_kind = "محله", f"محله: {value}", "oneHotOption"
    elif name in GENERAL_FEATURES:
        group, label_fa, input_kind = "مشخصات کلی", FEATURE_FA.get(name, name), "number"
    elif name in AREA_FEATURES:
        group, label_fa, input_kind = "مساحت‌ها", FEATURE_FA.get(name, name), "number"
    elif name in QUALITY_FEATURES or name.endswith("_encoded"):
        group, label_fa, input_kind = "کیفیت و وضعیت", FEATURE_FA.get(name, name.replace("_encoded", " کدگذاری‌شده")), "number"
    elif name in AMENITY_FEATURES:
        group, label_fa, input_kind = "امکانات", FEATURE_FA.get(name, name), "number"
    elif one_hot:
        group, label_fa, input_kind = "featureهای فنی", f"{prefix}: {value}", "oneHotOption"
    else:
        group, label_fa, input_kind = "featureهای فنی", FEATURE_FA.get(name, name), "number"
    unit = "sqft" if name in AREA_FEATURES or name.endswith("SF") or name == "LotArea" else "year" if "Year" in name or name == "YearBuilt" else ""
    return {
        "name": name,
        "labelFa": label_fa,
        "labelEn": name,
        "rawName": raw_name,
        "group": group,
        "unit": unit,
        "help": f"نام خام مدل: {raw_name}" + (f"؛ واحد: {unit}" if unit else ""),
        "inputKind": input_kind,
        "oneHotGroup": prefix if input_kind == "oneHotOption" else None,
        "oneHotValue": value if input_kind == "oneHotOption" else None,
        "type": "number",
        "default": 0,
    }

@app.get("/api/features")
def features(task: str = Query(...), dataset: str = Query(...), model: str = Query(...)):
    try:
        bundle = load_bundle(task, dataset, model)
        return {"features": [_feature_meta(f) for f in bundle["features"]]}
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.get("/api/presets")
@app.get("/presets")
def presets(task: str, dataset: str):
    try:
        return {"presets": list_presets(task, dataset)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/api/samples")
@app.get("/samples")
def samples(task: str, dataset: str, model: str, limit: int = 10):
    try:
        return {"samples": list_samples(task, dataset, model, limit)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/predict")
def predict_endpoint(req: PredictRequest):
    try:
        features = req.features
        if req.input_mode == "preset":
            if not req.preset_id:
                raise ValueError("preset_id is required for preset mode")
            features = preset_features(req.task, req.dataset, req.model, req.preset_id)
        elif req.input_mode == "dataset":
            if not req.sample_id:
                raise ValueError("sample_id is required for dataset mode")
            features = sample_features(req.task, req.dataset, req.model, req.sample_id)
        return predict(req.task, req.dataset, req.model, features)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/api/metrics")
def metrics(task: str, dataset: str, model: str):
    try:
        ev = evaluation(task, dataset, model)
        return {"metrics": ev["metrics"], "feature_importance": feature_importance(task, dataset, model)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/api/visualization")
def visualization(task: str, dataset: str, model: str):
    try:
        ev = evaluation(task, dataset, model)
        return {**ev, "feature_importance": feature_importance(task, dataset, model)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
