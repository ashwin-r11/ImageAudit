"""
Index images under backend/data/raw/, extract CV features, write labels.csv.

Expected layout (you populate):
  data/raw/normal/          # clean / acceptable images
  data/raw/blur/            # blurred images (e.g. CERTH)
  data/raw/defect/          # defective (e.g. MVTec anomalous)
  data/raw/underexposure/
  data/raw/overexposure/
  data/raw/noise/           # optional

Folder name becomes the label. Files directly under raw/ with no subfolder are skipped.
No download and no synthetic degradation generation.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import cv2

# Allow running as script: python -m app.training.build_dataset
BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.cv_features import extract_features  # noqa: E402

RAW_DIR = BACKEND_ROOT / "data" / "raw"
OUT_CSV = BACKEND_ROOT / "data" / "labels.csv"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

VALID_LABELS = {
    "normal",
    "clean",
    "blur",
    "defect",
    "underexposure",
    "overexposure",
    "noise",
    "corruption",
}


def iter_labeled_images(raw_dir: Path):
    if not raw_dir.exists():
        return
    for sub in sorted(raw_dir.iterdir()):
        if not sub.is_dir():
            continue
        label = sub.name.lower()
        if label not in VALID_LABELS:
            print(f"Skipping unknown folder: {sub.name}")
            continue
        # Normalize alias
        if label == "clean":
            label = "normal"
        for path in sorted(sub.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTS and path.is_file():
                yield path, label


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for path, label in iter_labeled_images(RAW_DIR):
        image = cv2.imread(str(path))
        if image is None:
            print(f"Unreadable, skip: {path}")
            continue
        try:
            feats = extract_features(image)
        except Exception as exc:  # noqa: BLE001
            print(f"Feature fail {path}: {exc}")
            continue
        rows.append(
            {
                "image_path": str(path.relative_to(BACKEND_ROOT)).replace("\\", "/"),
                "blur_score": feats["blur_score"],
                "brightness_mean": feats["brightness_mean"],
                "contrast": feats["contrast"],
                "noise_estimate": feats["noise_estimate"],
                "saturation_mean": feats["saturation_mean"],
                "label": label,
            }
        )
        print(f"OK {label}: {path.name}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "image_path",
        "blur_score",
        "brightness_mean",
        "contrast",
        "noise_estimate",
        "saturation_mean",
        "label",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    if not rows:
        print(
            "No images found. Place files under data/raw/<label>/ "
            "(normal, blur, defect, underexposure, overexposure, noise)."
        )


if __name__ == "__main__":
    main()
