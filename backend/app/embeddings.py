"""Frozen MobileNetV2 ImageNet embedding extractor (CPU)."""

from __future__ import annotations

import threading

import cv2
import numpy as np
import torch
from torchvision import models
from torchvision.models import MobileNet_V2_Weights

_lock = threading.Lock()
_model: torch.nn.Module | None = None
_preprocess = None
_device = torch.device("cpu")


def _ensure_model() -> tuple[torch.nn.Module, object]:
    global _model, _preprocess
    if _model is not None and _preprocess is not None:
        return _model, _preprocess
    with _lock:
        if _model is not None and _preprocess is not None:
            return _model, _preprocess
        weights = MobileNet_V2_Weights.IMAGENET1K_V1
        backbone = models.mobilenet_v2(weights=weights)
        # Feature vector before classifier: AdaptiveAvgPool → flatten (1280-d)
        backbone.classifier = torch.nn.Identity()
        backbone.eval()
        for p in backbone.parameters():
            p.requires_grad = False
        backbone.to(_device)
        _model = backbone
        _preprocess = weights.transforms()
        return _model, _preprocess


def get_embedding(image_bgr: np.ndarray) -> np.ndarray:
    """Return L2-normalized embedding from a BGR numpy image."""
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Empty or unreadable image")
    model, preprocess = _ensure_model()
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    # torchvision transforms expect PIL or tensor; convert via PIL
    from PIL import Image

    pil = Image.fromarray(rgb)
    tensor = preprocess(pil).unsqueeze(0).to(_device)
    with torch.no_grad():
        emb = model(tensor).squeeze(0).cpu().numpy().astype(np.float64)
    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
    return emb


def embedding_dim() -> int:
    model, _ = _ensure_model()
    # Probe once
    dummy = np.zeros((224, 224, 3), dtype=np.uint8)
    return int(get_embedding(dummy).shape[0])
