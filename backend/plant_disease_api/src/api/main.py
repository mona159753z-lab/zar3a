import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.predict import model_manager, run_prediction
from src.api.schemas import PredictResponse, HealthResponse, ErrorResponse


# ── Paths ─────────────────────────────────────────────────────
MODEL_PATH       = os.getenv("MODEL_PATH",       "models/best_model.pt")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "models/class_names.json")


# ── Startup / Shutdown ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown."""
    print("Starting up — loading model...")

    if Path(MODEL_PATH).exists() and Path(CLASS_NAMES_PATH).exists():
        model_manager.load(MODEL_PATH, CLASS_NAMES_PATH)
    else:
        print("No trained model found — loading dummy model for development.")
        model_manager.load_dummy(num_classes=38)

    yield

    print("Shutting down...")


# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title       = "Plant Disease Detector API",
    description = "Detect plant diseases from leaf images using EfficientNet-B3",
    version     = "1.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)


# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ── Routes ────────────────────────────────────────────────────
@app.get(
    "/health",
    response_model = HealthResponse,
    tags           = ["System"],
    summary        = "API health check",
)
async def health_check():
    """Check if API is running and model is loaded."""
    return HealthResponse(
        status       = "ok",
        model_loaded = model_manager.is_loaded,
        num_classes  = len(model_manager.class_names),
        device       = str(model_manager.device),
    )


@app.post(
    "/predict",
    response_model = PredictResponse,
    tags           = ["Prediction"],
    summary        = "Detect disease from leaf image",
    responses      = {
        400: {"model": ErrorResponse, "description": "Invalid image"},
        500: {"model": ErrorResponse, "description": "Model inference error"},
    },
)
async def predict(
    file: UploadFile = File(
        ...,
        description="Leaf image (JPG, PNG, WEBP — max 10MB)",
    ),
    include_gradcam: bool = Query(
        default=False,
        description="Include Grad-CAM heatmap in response",
    ),
):
    """
    Upload a leaf image and get:
    - Disease name + confidence score
    - Top 3 predictions
    - Treatment recommendations
    - Optional Grad-CAM visualization
    """
    if not model_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    try:
        image_bytes = await file.read()
        result = run_prediction(
            image_bytes     = image_bytes,
            filename        = file.filename,
            include_gradcam = include_gradcam,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.get(
    "/classes",
    tags    = ["System"],
    summary = "List all supported disease classes",
)
async def get_classes():
    """Return all 38 supported plant disease classes."""
    return {
        "num_classes": len(model_manager.class_names),
        "classes"    : model_manager.class_names,
    }


@app.get("/", tags=["System"], summary="Root endpoint")
async def root():
    return {
        "message": "Plant Disease Detector API",
        "docs"   : "/docs",
        "health" : "/health",
    }


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host    = "0.0.0.0",
        port    = 8000,
        reload  = True,
    )