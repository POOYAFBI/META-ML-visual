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
from .services.comparison import comparison
from .services.inputs import list_presets, list_samples, preset_features, sample_features
from .services.feature_metadata import feature_meta

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

@app.get("/api/features")
def features(task: str = Query(...), dataset: str = Query(...), model: str = Query(...)):
    try:
        bundle = load_bundle(task, dataset, model)
        return {"features": [feature_meta(f) for f in bundle["features"]]}
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.get("/api/presets")
def presets(task: str, dataset: str):
    try:
        return {"presets": list_presets(task, dataset)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/api/samples")
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

@app.get("/api/comparison")
def comparison_endpoint(task: str = Query(...)):
    try:
        return comparison(task)
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
