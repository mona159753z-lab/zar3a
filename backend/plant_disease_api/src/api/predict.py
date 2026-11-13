import time
import base64
import io
import json
import torch
import torch.nn.functional as F
from PIL import Image
from pathlib import Path
from typing import List

from src.model.efficientnet import PlantDiseaseModel, load_model, get_device
from src.model.grad_cam import GradCAM, overlay_to_pil
from src.utils.preprocessing import preprocess_image, validate_image, load_image_from_bytes
from src.utils.disease_info import get_disease_info, get_severity_color
from src.api.schemas import (
    PredictResponse,
    DiseasePrediction,
    DiseaseDetails,
)


# ── Model Singleton ───────────────────────────────────────────
class ModelManager:
    """
    Loads model once at startup and keeps it in memory.
    Prevents reloading on every request.
    """

    def __init__(self):
        self.model       : PlantDiseaseModel = None
        self.grad_cam    : GradCAM           = None
        self.class_names : List[str]         = []
        self.device      : torch.device      = get_device()
        self.is_loaded   : bool              = False

    def load(self, model_path: str, class_names_path: str) -> None:
        """Load model + class names from disk."""
        # Load class names
        with open(class_names_path, "r") as f:
            self.class_names = json.load(f)

        # Load model
        self.model = load_model(model_path, device=str(self.device))
        self.model.to(self.device)
        self.model.eval()

        # Initialize Grad-CAM
        self.grad_cam  = GradCAM(self.model)
        self.is_loaded = True

        print(f"Model ready — {len(self.class_names)} classes on {self.device}")

    def load_dummy(self, num_classes: int = 38) -> None:
        """Load untrained model for development/testing."""
        self.class_names = [f"Class_{i}" for i in range(num_classes)]
        self.model       = PlantDiseaseModel(num_classes=num_classes, pretrained=False)
        self.model.to(self.device)
        self.model.eval()
        self.grad_cam    = GradCAM(self.model)
        self.is_loaded   = True
        print("Dummy model loaded for development.")


# ── Global instance (loaded once at startup) ──────────────────
model_manager = ModelManager()


# ── Core Prediction ───────────────────────────────────────────
def run_prediction(
    image_bytes    : bytes,
    filename       : str,
    include_gradcam: bool = False,
) -> PredictResponse:
    """
    Full prediction pipeline:
    1. Validate image
    2. Preprocess
    3. Run model inference
    4. Build response with disease info
    5. Optionally generate Grad-CAM
    """

    # 1. Validate
    is_valid, error_msg = validate_image(filename, len(image_bytes))
    if not is_valid:
        raise ValueError(error_msg)

    # 2. Load image
    image = load_image_from_bytes(image_bytes)
    img_w, img_h = image.size

    # 3. Preprocess + inference
    tensor = preprocess_image(image).to(model_manager.device)

    start_time = time.time()
    with torch.no_grad():
        logits      = model_manager.model(tensor)          # (1, 38)
        probs       = F.softmax(logits, dim=1).squeeze(0)  # (38,)
    inference_ms = (time.time() - start_time) * 1000

    # 4. Top-3 predictions
    top3_probs, top3_idxs = torch.topk(probs, k=3)
    all_predictions = _build_predictions(top3_probs, top3_idxs)
    top_prediction  = all_predictions[0]

    # 5. Disease info
    disease_info = _build_disease_details(top_prediction.class_name)

    # 6. Grad-CAM (optional)
    gradcam_b64 = None
    if include_gradcam:
        gradcam_b64 = _generate_gradcam_b64(image, top3_idxs[0].item())

    return PredictResponse(
        top_prediction    = top_prediction,
        all_predictions   = all_predictions,
        disease_info      = disease_info,
        image_width       = img_w,
        image_height      = img_h,
        gradcam_image     = gradcam_b64,
        inference_time_ms = round(inference_ms, 2),
    )


# ── Helpers ──────────────────────────────────────────────────
def _build_predictions(
    probs: torch.Tensor,
    idxs : torch.Tensor,
) -> List[DiseasePrediction]:
    """Convert top-k tensors to DiseasePrediction list."""
    predictions = []
    for prob, idx in zip(probs.tolist(), idxs.tolist()):
        class_name = model_manager.class_names[idx]
        info       = get_disease_info(class_name)
        predictions.append(
            DiseasePrediction(
                class_name = class_name,
                disease    = info.name,
                plant      = info.plant,
                confidence = round(prob, 4),
            )
        )
    return predictions


def _build_disease_details(class_name: str) -> DiseaseDetails:
    """Build full DiseaseDetails from class name."""
    info = get_disease_info(class_name)
    return DiseaseDetails(
        name          = info.name,
        name_ar       = info.name_ar,
        plant         = info.plant,
        severity      = info.severity,
        severity_color= get_severity_color(info.severity),
        description   = info.description,
        treatments    = info.treatments,
        prevention    = info.prevention,
    )


def _generate_gradcam_b64(image: Image.Image, class_idx: int) -> str:
    """Generate Grad-CAM overlay and return as base64 PNG string."""
    _, overlay       = model_manager.grad_cam.generate(image, class_idx)
    overlay_pil      = overlay_to_pil(overlay)
    buffer           = io.BytesIO()
    overlay_pil.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")