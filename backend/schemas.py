from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    task: str
    dataset: str
    model: str
    features: dict[str, Any] = Field(default_factory=dict)
    input_mode: str = "advanced"
    preset_id: str | None = None
    sample_id: str | None = None


class ModelMetadata(BaseModel):
    model_name: str
    model_class: str | None = None
    task_type: str
    dataset_used: str


class PredictionAnalysis(BaseModel):
    reliability: str
    label: str
    explanation: str


class PredictionRange(BaseModel):
    lower: float
    upper: float
    basis: str
    metric: str
    metric_value: float


class ErrorEstimate(BaseModel):
    metric: str
    value: float
    description: str


class PredictResponse(BaseModel):
    prediction: float | int
    model_metadata: ModelMetadata
    confidence: float
    analysis: PredictionAnalysis

    error_estimate: ErrorEstimate | None = None
    prediction_range: PredictionRange | None = None
    confidence_basis: str | None = None
    confidence_label: str | None = None
    confidence_explanation: str | None = None

    predicted_class: int | None = None
    class_probabilities: dict[str, float] | None = None


class FeaturesResponse(BaseModel):
    features: list[dict[str, Any]]


class MetricsResponse(BaseModel):
    metrics: dict[str, float]
    feature_importance: list[dict[str, Any]]


class PresetsResponse(BaseModel):
    presets: list[dict[str, Any]]


class SamplesResponse(BaseModel):
    samples: list[dict[str, Any]]


class ComparisonResponse(BaseModel):
    task: str
    primary_metric: str
    primary_metric_direction: str
    rows: list[dict[str, Any]]
    summary_cards: list[dict[str, Any]]
    best: dict[str, Any]
    insights: dict[str, str]
    metric_definitions: dict[str, dict[str, Any]]
    chart_config: list[dict[str, str]]


class VisualizationResponse(BaseModel):
    metrics: dict[str, float]
    actual: list[Any]
    predicted: list[Any]
    errors: list[Any]
    feature_importance: list[dict[str, Any]]
    error_definition: str | None = None
    error_unit: str | None = None
    ideal_line_description: str | None = None
    is_correct: list[bool] | None = None
    actual_class: list[Any] | None = None
    predicted_class: list[Any] | None = None
    class_labels: dict[str, str] | None = None
