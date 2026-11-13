import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
from typing import Tuple

from src.model.efficientnet import PlantDiseaseModel
from src.utils.preprocessing import preprocess_image, tensor_to_numpy


# ── Grad-CAM ─────────────────────────────────────────────────
class GradCAM:
    """
    Gradient-weighted Class Activation Mapping.
    Highlights the regions of the image the model focused on.
    
    Usage:
        cam = GradCAM(model)
        heatmap, overlay = cam.generate(image, class_idx)
    """

    def __init__(self, model: PlantDiseaseModel):
        self.model       = model
        self.gradients   = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        """Hook into last conv block of EfficientNet backbone."""
        target_layer = self.model.backbone.blocks[-1]

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(
        self,
        image: Image.Image,
        class_idx: int = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Grad-CAM heatmap for given image.
        
        Args:
            image     : PIL Image (original, not preprocessed)
            class_idx : Target class index. If None, uses predicted class.
        
        Returns:
            heatmap   : Normalized heatmap (H, W) float32
            overlay   : Heatmap blended on original image (H, W, 3) uint8
        """
        self.model.eval()

        # Preprocess
        tensor = preprocess_image(image)   # (1, 3, 300, 300)
        tensor.requires_grad_(True)

        # Forward pass
        output = self.model(tensor)        # (1, 38)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        # Backward pass for target class
        self.model.zero_grad()
        score = output[0, class_idx]
        score.backward()

        # Compute Grad-CAM
        weights    = self.gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)
        cam        = (weights * self.activations).sum(dim=1)         # (1, H, W)
        cam        = F.relu(cam).squeeze(0).cpu().numpy()            # (H, W)

        # Normalize to [0, 1]
        cam = _normalize(cam)

        # Resize to original image size
        orig_w, orig_h = image.size
        heatmap = cv2.resize(cam, (orig_w, orig_h))

        # Create colored overlay
        overlay = _create_overlay(image, heatmap)

        return heatmap, overlay


# ── Helpers ──────────────────────────────────────────────────
def _normalize(arr: np.ndarray) -> np.ndarray:
    """Normalize array to [0, 1]."""
    arr_min, arr_max = arr.min(), arr.max()
    if arr_max - arr_min == 0:
        return np.zeros_like(arr)
    return (arr - arr_min) / (arr_max - arr_min)


def _create_overlay(
    image: Image.Image,
    heatmap: np.ndarray,
    alpha: float = 0.4,
) -> np.ndarray:
    """
    Blend heatmap with original image.
    
    Args:
        image   : Original PIL image
        heatmap : Normalized heatmap (H, W) in [0, 1]
        alpha   : Heatmap opacity (0 = invisible, 1 = full)
    
    Returns:
        overlay : Blended image (H, W, 3) uint8
    """
    # Convert PIL to numpy RGB
    img_np = np.array(image.convert("RGB"))

    # Apply colormap to heatmap
    heatmap_uint8  = np.uint8(255 * heatmap)
    heatmap_color  = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_rgb    = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Blend
    overlay = cv2.addWeighted(img_np, 1 - alpha, heatmap_rgb, alpha, 0)
    return overlay


def overlay_to_pil(overlay: np.ndarray) -> Image.Image:
    """Convert numpy overlay back to PIL Image."""
    return Image.fromarray(overlay.astype(np.uint8))


# ── Quick Test ────────────────────────────────────────────────
if __name__ == "__main__":
    from src.model.efficientnet import PlantDiseaseModel

    model  = PlantDiseaseModel(pretrained=False)
    cam    = GradCAM(model)
    image  = Image.new("RGB", (300, 300), color=(34, 139, 34))

    heatmap, overlay = cam.generate(image)
    print(f"Heatmap shape : {heatmap.shape}")
    print(f"Overlay shape : {overlay.shape}")
    print("Grad-CAM working correctly!")