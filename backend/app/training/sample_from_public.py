"""
Build a capped labels.csv from sample_images/ public datasets (not the full trees).

Sources (seed=42):
  CERTH TrainingSet/Undistorted          -> normal (40)
  CERTH Naturally + Artificially Blurred -> blur (30)
  SIDD NOISY_SRGB_*.PNG                  -> noise (20)
  SIDD GT_SRGB_*.PNG                     -> normal (10)
  koniq10k                               -> normal (40) + under (15) + over (15) via brightness
  sample_images/{acceptable,blur,...}    -> include all small demo folders if present

Writes backend/data/labels.csv with paths relative to backend/ (../sample_images/...).
"""

from __future__ import annotations

import csv
import os
import random
import sys
from pathlib import Path

import cv2

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.cv_features import (  # noqa: E402
    BRIGHTNESS_OVER_LOW,
    BRIGHTNESS_UNDER_LOW,
    extract_features,
)

SAMPLE_ROOT = REPO_ROOT / "sample_images"
OUT_CSV = BACKEND_ROOT / "data" / "labels.csv"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

# Caps from plan
CAP_CERTH_NORMAL = 40
CAP_CERTH_BLUR = 30
CAP_SIDD_NOISE = 20
CAP_SIDD_GT_NORMAL = 10
CAP_KONIQ_NORMAL = 40
CAP_KONIQ_UNDER = 15
CAP_KONIQ_OVER = 15
KONIQ_SCAN_POOL = 500  # candidates scanned for exposure labeling

RNG = random.Random(42)


def rel_to_backend(path: Path) -> str:
    """Path relative to backend/, using .. for repo-level sample_images/."""
    return Path(os.path.relpath(path.resolve(), BACKEND_ROOT.resolve())).as_posix()


def list_images(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    out: list[Path] = []
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            out.append(p)
    return out


def sample_cap(paths: list[Path], n: int) -> list[Path]:
    if len(paths) <= n:
        return list(paths)
    return RNG.sample(paths, n)


def brightness_mean(path: Path) -> float | None:
    img = cv2.imread(str(path))
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(gray.mean())


def collect_labeled_paths() -> list[tuple[Path, str]]:
    pairs: list[tuple[Path, str]] = []

    # --- CERTH ---
    certh = SAMPLE_ROOT / "CERTH_ImageBlurDataset" / "TrainingSet"
    undistorted = list_images(certh / "Undistorted")
    for p in sample_cap(undistorted, CAP_CERTH_NORMAL):
        pairs.append((p, "normal"))

    blurred = list_images(certh / "Naturally-Blurred") + list_images(
        certh / "Artificially-Blurred"
    )
    for p in sample_cap(blurred, CAP_CERTH_BLUR):
        pairs.append((p, "blur"))

    # --- SIDD ---
    sidd_data = SAMPLE_ROOT / "SIDD_Small_sRGB_Only" / "Data"
    noisy: list[Path] = []
    gt: list[Path] = []
    if sidd_data.exists():
        for p in sidd_data.rglob("*"):
            if not p.is_file():
                continue
            name = p.name.upper()
            if name.startswith("NOISY_") and p.suffix.lower() == ".png":
                noisy.append(p)
            elif name.startswith("GT_") and p.suffix.lower() == ".png":
                gt.append(p)
    for p in sample_cap(noisy, CAP_SIDD_NOISE):
        pairs.append((p, "noise"))
    for p in sample_cap(gt, CAP_SIDD_GT_NORMAL):
        pairs.append((p, "normal"))

    # --- koniq: scan pool, split by brightness ---
    koniq_dir = SAMPLE_ROOT / "koniq10k_512x384"
    koniq_all = [p for p in koniq_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS] if koniq_dir.exists() else []
    if not koniq_all and koniq_dir.exists():
        koniq_all = list_images(koniq_dir)
    pool = sample_cap(koniq_all, min(KONIQ_SCAN_POOL, len(koniq_all))) if koniq_all else []

    under_cands: list[Path] = []
    over_cands: list[Path] = []
    mid_cands: list[Path] = []
    for p in pool:
        b = brightness_mean(p)
        if b is None:
            continue
        if b < BRIGHTNESS_UNDER_LOW:
            under_cands.append(p)
        elif b > BRIGHTNESS_OVER_LOW:
            over_cands.append(p)
        else:
            mid_cands.append(p)

    for p in sample_cap(under_cands, CAP_KONIQ_UNDER):
        pairs.append((p, "underexposure"))
    for p in sample_cap(over_cands, CAP_KONIQ_OVER):
        pairs.append((p, "overexposure"))
    for p in sample_cap(mid_cands, CAP_KONIQ_NORMAL):
        pairs.append((p, "normal"))

    # --- small demo folders (all files) ---
    demo_map = {
        "acceptable": "normal",
        "blur": "blur",
        "defect": "defect",
        "noise": "noise",
        "underexposure": "underexposure",
        "overexposure": "overexposure",
    }
    for folder_name, label in demo_map.items():
        for p in list_images(SAMPLE_ROOT / folder_name):
            # skip if already huge nested datasets mistaken as demo — only top-level small dirs
            if "CERTH" in p.parts or "SIDD" in p.parts or "koniq" in str(p).lower():
                continue
            pairs.append((p, label))

    # de-dupe by resolved path (keep first label)
    seen: set[Path] = set()
    unique: list[tuple[Path, str]] = []
    for p, label in pairs:
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        unique.append((p, label))
    return unique


def main() -> None:
    if not SAMPLE_ROOT.exists():
        raise SystemExit(f"Missing {SAMPLE_ROOT}")

    pairs = collect_labeled_paths()
    rows = []
    for path, label in pairs:
        img = cv2.imread(str(path))
        if img is None:
            print(f"Skip unreadable: {path}")
            continue
        # SIDD full-res can be huge — downscale for feature extraction speed only
        h, w = img.shape[:2]
        if max(h, w) > 1024:
            scale = 1024 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        try:
            feats = extract_features(img)
        except Exception as exc:  # noqa: BLE001
            print(f"Feature fail {path.name}: {exc}")
            continue
        rows.append(
            {
                "image_path": rel_to_backend(path),
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

    from collections import Counter

    counts = Counter(r["label"] for r in rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print("Counts:", dict(counts))


if __name__ == "__main__":
    main()
