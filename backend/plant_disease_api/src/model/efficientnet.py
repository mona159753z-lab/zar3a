import torch
import torch.nn as nn
import timm
from pathlib import Path


# ── Constants ──────────────────────────────────────────────
NUM_CLASSES  = 38
MODEL_NAME   = "efficientnet_b3"
DROPOUT_RATE = 0.3


# ── Model ───────────────────────────────────────────────────
class PlantDiseaseModel(nn.Module):
    """
    EfficientNet-B3 fine-tuned for plant disease classification.
    
    Architecture:
        - Backbone : EfficientNet-B3 pretrained on ImageNet
        - Dropout  : 0.3 (reduces overfitting)
        - Head     : Linear(1536 → 38 classes)
    """

    def __init__(self, num_classes: int = NUM_CLASSES, pretrained: bool = True):
        super().__init__()

        # Load backbone (pretrained on ImageNet)
        self.backbone = timm.create_model(
            MODEL_NAME,
            pretrained=pretrained,
            num_classes=0,      # remove original classifier
            global_pool="avg",
        )

        # Get feature dimension from backbone
        feature_dim = self.backbone.num_features  # 1536 for B3

        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Dropout(p=DROPOUT_RATE),
            nn.Linear(feature_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)        # (B, 1536)
        logits   = self.classifier(features)  # (B, 38)
        return logits

    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features before classifier (used for Grad-CAM)."""
        return self.backbone(x)


# ── Freeze / Unfreeze ────────────────────────────────────────
def freeze_backbone(model: PlantDiseaseModel) -> None:
    """Freeze backbone — train classifier head only (Phase 1)."""
    for param in model.backbone.parameters():
        param.requires_grad = False
    print("Backbone frozen. Training classifier head only.")


def unfreeze_backbone(model: PlantDiseaseModel) -> None:
    """Unfreeze all layers for full fine-tuning (Phase 2)."""
    for param in model.backbone.parameters():
        param.requires_grad = True
    print("All layers unfrozen. Full fine-tuning enabled.")


def unfreeze_last_n_blocks(model: PlantDiseaseModel, n: int = 3) -> None:
    """Unfreeze only last N blocks — good middle ground (Phase 1.5)."""
    blocks = list(model.backbone.blocks.children())
    for block in blocks[-n:]:
        for param in block.parameters():
            param.requires_grad = True
    print(f"Last {n} blocks unfrozen.")


# ── Save / Load ──────────────────────────────────────────────
def save_model(model: PlantDiseaseModel, path: str, metadata: dict = None) -> None:
    """Save model weights + optional metadata."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state_dict" : model.state_dict(),
        "num_classes"      : NUM_CLASSES,
        "model_name"       : MODEL_NAME,
        "metadata"         : metadata or {},
    }
    torch.save(checkpoint, path)
    print(f"Model saved → {path}")


def load_model(path: str, device: str = "cpu") -> PlantDiseaseModel:
    """Load model from checkpoint file."""
    checkpoint = torch.load(path, map_location=device)
    
    model = PlantDiseaseModel(
        num_classes=NUM_CLASSES,
        pretrained=False,
    )
    
    # Handle both formats
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    print(f"Model loaded from {path}")
    return model
# ── Device Helper ────────────────────────────────────────────
def get_device() -> torch.device:
    """Return best available device."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("Using CPU")
    return device


# ── Model Summary ────────────────────────────────────────────
def count_parameters(model: PlantDiseaseModel) -> None:
    """Print trainable vs total parameters."""
    total     = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total params    : {total:,}")
    print(f"Trainable params: {trainable:,}")
    print(f"Frozen params   : {total - trainable:,}")