"""
Pydantic schemas for Cyber IDS API endpoints.

Defines request/response models for:
- POST /ml/train: Training configuration and results
- POST /ml/predict: Flow features and predictions
- GET /ml/metrics: Metrics retrieval
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator


# ==================== Training Schemas ====================

class TrainRequest(BaseModel):
    """Request schema for training endpoint."""

    train_days: Optional[List[str]] = Field(
        None,
        description="List of day identifiers for training (e.g., ['Wednesday-14-02-2018'])",
        example=["Wednesday-14-02-2018", "Thursday-15-02-2018"],
    )
    val_days: Optional[List[str]] = Field(
        None,
        description="List of day identifiers for validation",
        example=["Wednesday-21-02-2018"],
    )
    test_days: Optional[List[str]] = Field(
        None,
        description="Optional list of day identifiers for test evaluation",
        example=["Thursday-22-02-2018"],
    )
    calibration_method: Optional[str] = Field(
        "isotonic",
        description="Calibration method: 'sigmoid' (Platt) or 'isotonic'",
        example="isotonic",
    )
    random_seed: Optional[int] = Field(
        42, description="Random seed for reproducibility", example=42
    )

    @validator("calibration_method")
    def validate_calibration_method(cls, v):
        if v not in ["sigmoid", "isotonic"]:
            raise ValueError("calibration_method must be 'sigmoid' or 'isotonic'")
        return v


class MetricsEntry(BaseModel):
    """Metrics bundle schema."""

    pr_auc_macro: float = Field(..., description="Precision-Recall AUC (macro)")
    recall_at_fpr_1pct: float = Field(..., description="Recall at 1% FPR")
    recall_at_fpr_0_1pct: Optional[float] = Field(None, description="Recall at 0.1% FPR")
    f1_macro: float = Field(..., description="F1 score (macro-averaged)")
    precision_macro: float = Field(..., description="Precision (macro-averaged)")
    recall_macro: float = Field(..., description="Recall (macro-averaged)")
    roc_auc: float = Field(..., description="ROC-AUC score")
    brier_score: float = Field(..., description="Brier score (calibration metric)")
    f1_attack: Optional[float] = Field(None, description="F1 for attack class")
    precision_attack: Optional[float] = Field(None, description="Precision for attack class")
    recall_attack: Optional[float] = Field(None, description="Recall for attack class")


class TrainResponse(BaseModel):
    """Response schema for training endpoint."""

    success: bool = Field(..., description="Whether training succeeded")
    champion: str = Field(..., description="Name of selected champion model")
    model_version: str = Field(..., description="Model version timestamp")
    metrics: MetricsEntry = Field(..., description="Validation metrics")
    artifact_paths: Dict[str, str] = Field(..., description="Paths to saved artifacts")
    elapsed_seconds: float = Field(..., description="Training time in seconds")
    message: Optional[str] = Field(None, description="Additional info or warnings")


# ==================== Prediction Schemas ====================

class FlowFeatures(BaseModel):
    """
    Network flow features schema.

    Accepts a flexible dictionary of CICFlowMeter features.
    Example keys: "Fwd Packet Length Mean", "Bwd Packet Length Max", etc.
    """

    features: Dict[str, float] = Field(
        ...,
        description="Dictionary of feature name → value",
        example={
            "Fwd Packet Length Mean": 123.45,
            "Bwd Packet Length Max": 567.89,
            "Flow Duration": 1000.0,
        },
    )


class PredictRequest(BaseModel):
    """Request schema for prediction endpoint."""

    flows: List[Dict[str, float]] = Field(
        ...,
        description="List of flow feature dictionaries",
        example=[
            {"Fwd Packet Length Mean": 123.45, "Flow Duration": 1000.0},
            {"Fwd Packet Length Mean": 200.0, "Flow Duration": 5000.0},
        ],
    )
    threshold: Optional[float] = Field(
        None,
        description="Decision threshold override (default: 0.5)",
        ge=0.0,
        le=1.0,
        example=0.5,
    )

    @validator("flows")
    def validate_flows(cls, v):
        if len(v) == 0:
            raise ValueError("flows list cannot be empty")
        if len(v) > 100:
            raise ValueError("flows list cannot exceed 100 items per request")
        return v


class PredictionItem(BaseModel):
    """Single flow prediction result."""

    label: int = Field(..., description="Predicted label (0=Benign, 1=Attack)")
    prob: float = Field(..., description="Predicted probability of attack", ge=0.0, le=1.0)
    model_version: str = Field(..., description="Model version used for prediction")


class PredictResponse(BaseModel):
    """Response schema for prediction endpoint."""

    predictions: List[PredictionItem] = Field(..., description="List of predictions")
    count: int = Field(..., description="Number of predictions")
    latency_ms: Optional[float] = Field(None, description="Prediction latency in milliseconds")


# ==================== Metrics Retrieval Schemas ====================

class PerFamilyMetrics(BaseModel):
    """Per-attack-family metrics."""

    precision: float
    recall: float
    f1: float
    count: int = Field(..., description="Number of samples in this family")


class MetricsResponse(BaseModel):
    """Response schema for metrics retrieval."""

    latest_version: str = Field(..., description="Version of latest trained model")
    metrics: MetricsEntry = Field(..., description="Validation metrics")
    per_family: Optional[Dict[str, PerFamilyMetrics]] = Field(
        None, description="Per-attack-family metrics"
    )
    latency_stats: Optional[Dict[str, float]] = Field(
        None, description="Prediction latency statistics (p50, p95)"
    )


# ==================== Health/Status Schemas ====================

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status", example="healthy")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_version: Optional[str] = Field(None, description="Loaded model version")
    n_features: Optional[int] = Field(None, description="Number of features")

