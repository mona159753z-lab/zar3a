from pydantic import BaseModel, Field
from typing import List, Optional


# ── Request ──────────────────────────────────────────────────
class PredictRequest(BaseModel):
    """Schema for prediction request metadata."""
    include_gradcam: bool = Field(
        default=False,
        description="Whether to include Grad-CAM heatmap in response",
    )


# ── Individual Prediction ─────────────────────────────────────
class DiseasePrediction(BaseModel):
    """Single disease prediction with confidence score."""
    class_name : str   = Field(..., description="Raw class name from model")
    disease    : str   = Field(..., description="Human-readable disease name")
    plant      : str   = Field(..., description="Plant type")
    confidence : float = Field(..., description="Confidence score 0-1", ge=0, le=1)


# ── Disease Details ───────────────────────────────────────────
class DiseaseDetails(BaseModel):
    """Full disease information for top prediction."""
    name        : str       = Field(..., description="Disease name in English")
    name_ar     : str       = Field(..., description="Disease name in Arabic")
    plant       : str       = Field(..., description="Affected plant")
    severity    : str       = Field(..., description="Severity: low / medium / high")
    severity_color: str     = Field(..., description="Hex color for severity")
    description : str       = Field(..., description="Short disease description")
    treatments  : List[str] = Field(..., description="List of treatment steps")
    prevention  : List[str] = Field(..., description="List of prevention tips")


# ── Full Response ─────────────────────────────────────────────
class PredictResponse(BaseModel):
    """Full API response for a plant disease prediction."""

    # Top prediction
    top_prediction : DiseasePrediction = Field(..., description="Highest confidence prediction")

    # Top 3 predictions
    all_predictions: List[DiseasePrediction] = Field(
        ..., description="Top 3 predictions with confidence scores"
    )

    # Disease info
    disease_info: DiseaseDetails = Field(..., description="Detailed disease information")

    # Image metadata
    image_width : int = Field(..., description="Original image width in pixels")
    image_height: int = Field(..., description="Original image height in pixels")

    # Optional Grad-CAM
    gradcam_image: Optional[str] = Field(
        default=None,
        description="Base64-encoded Grad-CAM overlay image (PNG)",
    )

    # Processing info
    inference_time_ms: float = Field(..., description="Model inference time in milliseconds")
    model_version     : str  = Field(default="efficientnet_b3_v1")


# ── Health Check ──────────────────────────────────────────────
class HealthResponse(BaseModel):
    """API health check response."""
    status      : str  = Field(default="ok")
    model_loaded: bool = Field(..., description="Whether model is loaded in memory")
    num_classes : int  = Field(..., description="Number of supported disease classes")
    device      : str  = Field(..., description="CPU or GPU")


# ── Error ─────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    """Standard error response."""
    error  : str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail : Optional[str] = Field(default=None, description="Technical details")