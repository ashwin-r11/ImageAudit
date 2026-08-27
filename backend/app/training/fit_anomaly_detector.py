"""
Fit IsolationForest on embeddings of normal/clean images; save anomaly_detector.joblib.

Uses labels.csv if present; otherwise scans data/raw/normal/.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import cv2
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.embeddings import get_embedding  # noqa: E402

LABELS_CSV = BACKEND_ROOT / "data" / "labels.csv"
RAW_NORMAL = BACKEND_ROOT / "data" / "raw" / "normal"
SAMPLE_DIR = BACKEND_ROOT.parent / "sample_images" / "acceptable"
MODEL_PATH = BACKEND_ROOT / "model" / "anomaly_detector.joblib"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def resolve_image_path(rel: str) -> Path:
    """Resolve labels.csv path relative to backend/ (supports ../sample_images/...)."""
    return (BACKEND_ROOT / rel).resolve()


def collect_normal_paths() -> list[Path]:
    paths: list[Path] = []
    if LABELS_CSV.exists():
        with LABELS_CSV.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("label", "").lower() in {"normal", "clean"}:
                    p = resolve_image_path(row["image_path"])
                    if p.exists():
                        paths.append(p)
    if not paths and RAW_NORMAL.exists():
        for p in RAW_NORMAL.rglob("*"):
            if p.suffix.lower() in IMAGE_EXTS and p.is_file():
                paths.append(p)
    if not paths and SAMPLE_DIR.exists():
        for p in SAMPLE_DIR.rglob("*"):
            if p.suffix.lower() in IMAGE_EXTS and p.is_file():
                paths.append(p)
    return paths


def load_image_bgr(path: Path):
    """Load image; downscale very large SIDD frames for embedding speed."""
    img = cv2.imread(str(path))
    if img is None:
        return None
    h, w = img.shape[:2]
    if max(h, w) > 1024:
        scale = 1024 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def main() -> None:
    paths = collect_normal_paths()
    if len(paths) < 3:
        raise SystemExit(
            f"Need at least 3 normal images to fit IsolationForest; found {len(paths)}. "
            "Run: python -m app.training.sample_from_public"
        )

    embeddings = []
    for p in paths:
        img = load_image_bgr(p)
        if img is None:
            print(f"Skip unreadable: {p}")
            continue
        emb = get_embedding(img)
        embeddings.append(emb)
        print(f"Embedded: {p.name}")

    X = np.vstack(embeddings)
    # contamination low — most training images are normal
    detector = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=1,
    )
    detector.fit(X)
    train_decisions = detector.decision_function(X)
    train_decision_mean = float(np.mean(train_decisions))
    train_decision_std = float(np.std(train_decisions)) or 0.05

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "detector": detector,
        "backbone": "mobilenet_v2_IMAGENET1K_V1",
        "n_train": int(X.shape[0]),
        "embedding_dim": int(X.shape[1]),
        "train_decision_mean": train_decision_mean,
        "decision_scale": max(train_decision_std, 0.02),
    }
    joblib.dump(payload, MODEL_PATH)
    print(
        f"Saved {MODEL_PATH} (n_train={X.shape[0]}, dim={X.shape[1]}, "
        f"train_decision_mean={train_decision_mean:.4f})"
    )


if __name__ == "__main__":
    main()
