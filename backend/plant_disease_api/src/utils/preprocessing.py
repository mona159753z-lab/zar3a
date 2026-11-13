import io
from PIL import Image
import torch
from torchvision import transforms
from typing import Tuple
import numpy as np


# ── Constants ──────────────────────────────────────────────
IMAGE_SIZE = 300
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


# ── Transforms ─────────────────────────────────────────────
def get_train_transforms() -> transforms.Compose:
    """Augmentation pipeline for training."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE + 20, IMAGE_SIZE + 20)),
        transforms.RandomCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(
            brightness=0.3,
            contrast=0.3,
            saturation=0.3,
            hue=0.1,
        ),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transforms() -> transforms.Compose:
    """Clean pipeline for validation and inference — no augmentation."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# ── Image Loading ───────────────────────────────────────────
def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """Load a PIL image from raw bytes (used in FastAPI endpoint)."""
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def load_image_from_path(path: str) -> Image.Image:
    """Load a PIL image from file path."""
    image = Image.open(path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


# ── Preprocessing ───────────────────────────────────────────
def preprocess_image(image: Image.Image) -> torch.Tensor:
    """
    Convert PIL image → normalized tensor ready for model.
    Returns shape: (1, 3, 300, 300)
    """
    transform = get_val_transforms()
    tensor = transform(image)          # (3, 300, 300)
    return tensor.unsqueeze(0)         # (1, 3, 300, 300)


def tensor_to_numpy(tensor: torch.Tensor) -> np.ndarray:
    """Convert tensor back to numpy array for visualization."""
    arr = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    arr = arr * IMAGENET_STD + IMAGENET_MEAN   # denormalize
    return np.clip(arr, 0, 1)


# ── Validation ──────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_MB   = 10


def validate_image(filename: str, file_size_bytes: int) -> Tuple[bool, str]:
    """
    Validate uploaded image before processing.
    Returns (is_valid, error_message).
    """
    import os
    ext = os.path.splitext(filename)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported format '{ext}'. Use: {ALLOWED_EXTENSIONS}"

    size_mb = file_size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({size_mb:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB"

    return True, ""