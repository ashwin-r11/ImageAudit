"""FastAPI application — ImageAudit backend."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import anomaly_model
from .database import Base, engine, get_db
from .models import AnalysisResult
from .schemas import AnalysisResultOut, HealthOut, HistoryEntryOut

BACKEND_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BACKEND_ROOT / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_API_BASE = os.getenv("PUBLIC_API_BASE", "http://localhost:8000").rstrip("/")

app = FastAPI(title="ImageAudit API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    anomaly_model.load_detector()


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", model_loaded=anomaly_model.model_loaded())


def _decode_image(data: bytes) -> np.ndarray:
    if not data:
        raise HTTPException(status_code=400, detail="Empty file upload")
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Unreadable or invalid image file")
    return image


@app.post("/analyze", response_model=AnalysisResultOut)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> AnalysisResultOut:
    content_type = (file.content_type or "").lower()
    if content_type and not (
        content_type.startswith("image/") or content_type == "application/octet-stream"
    ):
        raise HTTPException(status_code=400, detail="File must be an image")

    raw = await file.read()
    try:
        image = _decode_image(raw)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Unreadable or invalid image file") from None

    if not anomaly_model.model_loaded():
        # Attempt reload in case model was fitted after startup
        anomaly_model.load_detector()
    if not anomaly_model.model_loaded():
        raise HTTPException(
            status_code=500,
            detail="Anomaly model not loaded. Run training/fit_anomaly_detector.py first.",
        )

    try:
        result = anomaly_model.analyze_image(image)
    except Exception:
        raise HTTPException(status_code=500, detail="Analysis failed") from None

    ext = Path(file.filename or "upload.jpg").suffix.lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename
    dest.write_bytes(raw)
    thumbnail_url = f"{PUBLIC_API_BASE}/uploads/{filename}"

    row = AnalysisResult(
        quality_score=result["quality_score"],
        quality_label=result["quality_label"],
        issues_json=json.dumps(result["issues"]),
        image_stats_json=json.dumps(result["image_stats"]),
        explanation=result.get("explanation"),
        image_path=str(dest),
        thumbnail_url=thumbnail_url,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return AnalysisResultOut(
        id=row.id,
        quality_score=row.quality_score,
        quality_label=row.quality_label,  # type: ignore[arg-type]
        issues=result["issues"],
        image_stats=result["image_stats"],
        explanation=row.explanation,
    )


@app.get("/results/{result_id}", response_model=AnalysisResultOut)
def get_result(result_id: int, db: Session = Depends(get_db)) -> AnalysisResultOut:
    row = db.get(AnalysisResult, result_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    return AnalysisResultOut(
        id=row.id,
        quality_score=row.quality_score,
        quality_label=row.quality_label,  # type: ignore[arg-type]
        issues=json.loads(row.issues_json),
        image_stats=json.loads(row.image_stats_json),
        explanation=row.explanation,
    )


@app.get("/history", response_model=list[HistoryEntryOut])
def history(db: Session = Depends(get_db), limit: int = 50) -> list[HistoryEntryOut]:
    limit = max(1, min(limit, 200))
    rows = (
        db.query(AnalysisResult)
        .order_by(AnalysisResult.created_at.desc())
        .limit(limit)
        .all()
    )
    out: list[HistoryEntryOut] = []
    for row in rows:
        created = row.created_at.isoformat() if row.created_at else ""
        out.append(
            HistoryEntryOut(
                id=row.id,
                quality_label=row.quality_label,  # type: ignore[arg-type]
                quality_score=row.quality_score,
                created_at=created,
                thumbnail_url=row.thumbnail_url,
            )
        )
    return out
