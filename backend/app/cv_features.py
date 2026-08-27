"""Classical OpenCV feature extraction and rule-based severity helpers."""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np

# Empirically tuned — separated sharp vs soft portraits better than first pass
# Blur: Laplacian variance; lower = blurrier. ~96 should be medium, ~345 clean.
BLUR_HIGH = 40.0
BLUR_MEDIUM = 120.0
BLUR_LOW = 200.0

# Underexposure: only flag clearly dark frames (mood portraits ~70 should pass)
BRIGHTNESS_UNDER_HIGH = 30.0
BRIGHTNESS_UNDER_MEDIUM = 50.0
BRIGHTNESS_UNDER_LOW = 65.0

BRIGHTNESS_OVER_HIGH = 220.0
BRIGHTNESS_OVER_MEDIUM = 200.0
BRIGHTNESS_OVER_LOW = 180.0

NOISE_HIGH = 45.0
NOISE_MEDIUM = 35.0
NOISE_LOW = 28.0

CORRUPTION_VARIANCE_MIN = 5.0


def extract_features(image_bgr: np.ndarray) -> dict[str, float | bool]:
    """Extract quality features from a BGR image array."""
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Empty or unreadable image")

    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_mean = float(np.mean(gray))
    brightness_std = float(np.std(gray))
    contrast = brightness_std

    median = cv2.medianBlur(gray, 5)
    noise_estimate = float(np.std(gray.astype(np.float64) - median.astype(np.float64)))

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    saturation_mean = float(np.mean(hsv[:, :, 1]))

    overall_var = float(np.var(gray))
    abnormal_dims = h < 16 or w < 16 or h > 10000 or w > 10000
    corruption_flag = bool(abnormal_dims or overall_var < CORRUPTION_VARIANCE_MIN)

    return {
        "blur_score": lap_var,
        "brightness_mean": brightness_mean,
        "brightness_std": brightness_std,
        "contrast": contrast,
        "noise_estimate": noise_estimate,
        "saturation_mean": saturation_mean,
        "corruption_flag": corruption_flag,
    }


def _severity_from_bands(
    value: float,
    *,
    worse_when_lower: bool,
    high: float,
    medium: float,
    low: float,
) -> str | None:
    """Return severity or None if within acceptable range."""
    if worse_when_lower:
        if value < high:
            return "high"
        if value < medium:
            return "medium"
        if value < low:
            return "low"
        return None
    if value > high:
        return "high"
    if value > medium:
        return "medium"
    if value > low:
        return "low"
    return None


def classify_feature_severities(features: dict[str, Any]) -> list[dict[str, Any]]:
    """Map features to issue dicts with type, severity, confidence (no 'none')."""
    issues: list[dict[str, Any]] = []

    blur_sev = _severity_from_bands(
        float(features["blur_score"]),
        worse_when_lower=True,
        high=BLUR_HIGH,
        medium=BLUR_MEDIUM,
        low=BLUR_LOW,
    )
    if blur_sev:
        conf = {"high": 0.9, "medium": 0.75, "low": 0.6}[blur_sev]
        issues.append({"type": "blur", "severity": blur_sev, "confidence": conf})

    under = _severity_from_bands(
        float(features["brightness_mean"]),
        worse_when_lower=True,
        high=BRIGHTNESS_UNDER_HIGH,
        medium=BRIGHTNESS_UNDER_MEDIUM,
        low=BRIGHTNESS_UNDER_LOW,
    )
    if under:
        conf = {"high": 0.88, "medium": 0.72, "low": 0.55}[under]
        issues.append({"type": "underexposure", "severity": under, "confidence": conf})

    over = _severity_from_bands(
        float(features["brightness_mean"]),
        worse_when_lower=False,
        high=BRIGHTNESS_OVER_HIGH,
        medium=BRIGHTNESS_OVER_MEDIUM,
        low=BRIGHTNESS_OVER_LOW,
    )
    if over:
        conf = {"high": 0.88, "medium": 0.72, "low": 0.55}[over]
        issues.append({"type": "overexposure", "severity": over, "confidence": conf})

    noise_sev = _severity_from_bands(
        float(features["noise_estimate"]),
        worse_when_lower=False,
        high=NOISE_HIGH,
        medium=NOISE_MEDIUM,
        low=NOISE_LOW,
    )
    if noise_sev:
        conf = {"high": 0.85, "medium": 0.7, "low": 0.55}[noise_sev]
        issues.append({"type": "noise", "severity": noise_sev, "confidence": conf})

    if features.get("corruption_flag"):
        issues.append({"type": "corruption", "severity": "high", "confidence": 0.95})

    return issues


def cv_penalty(issues: list[dict[str, Any]]) -> float:
    """Penalty points (0–70) subtracted from a base quality score.

    Blur is weighted heavier so soft images cannot sit within a few points of sharp ones.
    """
    default = {"low": 8.0, "medium": 16.0, "high": 26.0}
    blur_weights = {"low": 12.0, "medium": 28.0, "high": 40.0}
    total = 0.0
    for issue in issues:
        sev = issue["severity"]
        if issue.get("type") == "blur":
            total += blur_weights.get(sev, 12.0)
        else:
            total += default.get(sev, 8.0)
    return min(total, 70.0)
