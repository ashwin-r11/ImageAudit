from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    quality_label: Mapped[str] = mapped_column(String(32), nullable=False)
    issues_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    image_stats_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
