"""Load fitted anomaly detector and merge with CV features into API result payload."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from .cv_features import classify_feature_severities, cv_penalty, extract_features
from .embeddings import get_embedding

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = BACKEND_ROOT / "model" / "anomaly_detector.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))

_detector = None
_model_meta: dict[str, Any] = {}


def model_loaded() -> bool:
    return _detector is not None


def load_detector(path: Path | None = None) -> bool:
    """Load joblib artifact. Returns True if loaded."""
    global _detector, _model_meta
    target = path or MODEL_PATH
    if not target.exists():
        _detector = None
        _model_meta = {}
        return False
    payload = joblib.load(target)
    if isinstance(payload, dict) and "detector" in payload:
        _detector = payload["detector"]
        _model_meta = {k: v for k, v in payload.items() if k != "detector"}
    else:
        _detector = payload
        _model_meta = {}
    return True


def anomaly_score(embedding: np.ndarray) -> tuple[float, float]:
    """
    Returns (raw_decision, anomaly_confidence in [0,1]).
    IsolationForest: lower decision_function => more anomalous.
    Calibrated against training decision mean stored at fit time.
    """
    if _detector is None:
        return 0.0, 0.0
    x = embedding.reshape(1, -1)
    decision = float(_detector.decision_function(x)[0])
    train_mean = float(_model_meta.get("train_decision_mean", 0.0))
    # Positive delta => more anomalous than the typical training normal
    delta = train_mean - decision
    scale = float(_model_meta.get("decision_scale", 0.05)) or 0.05
    # Shift so images near the training mean score ~0.12, not ~0.5
    anomaly_conf = float(1.0 / (1.0 + np.exp(-(delta / scale - 2.0))))
    return decision, anomaly_conf


def quality_label_from_score(score: float) -> str:
    if score >= 70:
        return "ACCEPTABLE"
    if score >= 40:
        return "DEGRADED"
    return "DEFECTIVE"


def analyze_image(image_bgr: np.ndarray) -> dict[str, Any]:
    """Run hybrid inference; returns dict matching AnalysisResult fields (without id)."""
    features = extract_features(image_bgr)
    issues = classify_feature_severities(features)

    emb = get_embedding(image_bgr)
    decision, anomaly_conf = anomaly_score(emb)

    # Mild in-distribution anomaly (~0.15–0.30) should not dominate CV quality
    effective_anomaly = max(0.0, anomaly_conf - 0.18)
    base = 100.0 - effective_anomaly * 80.0
    penalty = cv_penalty(issues)
    quality_score = float(max(0.0, min(100.0, base - penalty)))

    # Visual defect issue when anomaly confidence is material
    if anomaly_conf >= 0.55:
        sev = "high" if anomaly_conf >= 0.75 else ("medium" if anomaly_conf >= 0.65 else "low")
        issues.append(
            {
                "type": "visual_defect",
                "severity": sev,
                "confidence": round(anomaly_conf, 3),
            }
        )
        if sev == "high":
            quality_score = min(quality_score, 35.0)
        elif sev == "medium":
            quality_score = min(quality_score, 55.0)

    if features.get("corruption_flag"):
        quality_score = min(quality_score, 25.0)

    label = quality_label_from_score(quality_score)

    fired = [f"{i['type']}({i['severity']})" for i in issues] or ["none"]
    explanation = (
        f"Hybrid score: embedding anomaly_conf={anomaly_conf:.3f} "
        f"(IsolationForest decision={decision:.4f}); "
        f"CV issues: {', '.join(fired)}; "
        f"quality_score={quality_score:.1f} -> {label}."
    )

    return {
        "quality_score": round(quality_score, 2),
        "quality_label": label,
        "issues": issues,
        "image_stats": {
            "blur_score": round(float(features["blur_score"]), 2),
            "brightness_mean": round(float(features["brightness_mean"]), 2),
            "contrast": round(float(features["contrast"]), 2),
            "noise_estimate": round(float(features["noise_estimate"]), 2),
        },
        "explanation": explanation,
    }
