"""
Evaluate anomaly detector on held-out normal vs non-normal images from labels.csv.

Metrics: ROC-AUC, precision/recall/F1 (anomaly as positive), confusion counts.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import joblib
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.embeddings import get_embedding  # noqa: E402

LABELS_CSV = BACKEND_ROOT / "data" / "labels.csv"
MODEL_PATH = BACKEND_ROOT / "model" / "anomaly_detector.joblib"
REPORT_PATH = BACKEND_ROOT / "model" / "eval_report.json"


def load_rows():
    if not LABELS_CSV.exists():
        raise SystemExit(f"Missing {LABELS_CSV}; run sample_from_public.py first.")
    rows = []
    with LABELS_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def resolve_image_path(rel: str) -> Path:
    return (BACKEND_ROOT / rel).resolve()


def load_image_bgr(path: Path):
    img = cv2.imread(str(path))
    if img is None:
        return None
    h, w = img.shape[:2]
    if max(h, w) > 1024:
        scale = 1024 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def main() -> None:
    if not MODEL_PATH.exists():
        raise SystemExit(f"Missing {MODEL_PATH}; run fit_anomaly_detector.py first.")

    payload = joblib.load(MODEL_PATH)
    detector = payload["detector"] if isinstance(payload, dict) else payload

    rows = load_rows()
    y_true = []
    y_score = []  # higher = more anomalous
    y_pred = []
    failures = []

    for row in rows:
        path = resolve_image_path(row["image_path"])
        if not path.exists():
            continue
        img = load_image_bgr(path)
        if img is None:
            continue
        emb = get_embedding(img).reshape(1, -1)
        decision = float(detector.decision_function(emb)[0])
        # anomaly score: invert decision
        score = float(-decision)
        pred_anom = int(detector.predict(emb)[0] == -1)
        is_anom = 0 if row["label"].lower() in {"normal", "clean"} else 1

        y_true.append(is_anom)
        y_score.append(score)
        y_pred.append(pred_anom)

        if pred_anom != is_anom:
            failures.append(
                {
                    "image_path": row["image_path"],
                    "label": row["label"],
                    "predicted_anomaly": bool(pred_anom),
                    "decision": decision,
                }
            )

    if not y_true or len(set(y_true)) < 2:
        report = {
            "note": "Need both normal and anomalous labeled rows for full metrics.",
            "n_evaluated": len(y_true),
            "y_true_unique": sorted(set(y_true)),
            "failures": failures[:20],
        }
    else:
        auc = float(roc_auc_score(y_true, y_score))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        cm = confusion_matrix(y_true, y_pred).tolist()
        report = {
            "n_evaluated": len(y_true),
            "roc_auc": auc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "confusion_matrix": {
                "labels": ["normal(0)", "anomaly(1)"],
                "matrix": cm,
            },
            "failure_cases_sample": failures[:20],
            "limitations": [
                "IsolationForest fitted on normal embeddings only (MobileNetV2 ImageNet).",
                "Capped subsets of CERTH / SIDD / koniq — not full-benchmark scores.",
                "Exposure labels from brightness thresholds can be circular with CV rules.",
            ],
        }
        print(f"ROC-AUC={auc:.3f}  P={prec:.3f}  R={rec:.3f}  F1={f1:.3f}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    if failures:
        print(f"Failure examples: {len(failures)} (see report)")


if __name__ == "__main__":
    main()
