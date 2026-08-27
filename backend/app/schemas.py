from typing import Literal

from pydantic import BaseModel, Field

QualityLabel = Literal["ACCEPTABLE", "DEGRADED", "DEFECTIVE"]
IssueSeverity = Literal["low", "medium", "high"]


class DetectedIssue(BaseModel):
    type: str
    severity: IssueSeverity
    confidence: float = Field(ge=0.0, le=1.0)


class ImageStats(BaseModel):
    blur_score: float
    brightness_mean: float
    contrast: float
    noise_estimate: float


class AnalysisResultOut(BaseModel):
    id: int
    quality_score: float
    quality_label: QualityLabel
    issues: list[DetectedIssue]
    image_stats: ImageStats
    explanation: str | None = None


class HistoryEntryOut(BaseModel):
    id: int
    quality_label: QualityLabel
    quality_score: float
    created_at: str
    thumbnail_url: str


class HealthOut(BaseModel):
    status: str
    model_loaded: bool
