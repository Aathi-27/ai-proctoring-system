from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.common import Recommendation, RiskClassification


class ScoreTimelinePoint(BaseModel):
    timestamp: datetime
    score: int = Field(ge=0, le=100)


class ReportEvent(BaseModel):
    event_id: str
    timestamp: datetime
    type: str
    confidence: float = Field(ge=0, le=1)
    risk_contribution: int = Field(ge=0)


class EvidenceSnapshotRef(BaseModel):
    snapshot_id: str
    timestamp: datetime
    event_type: str
    s3_url: str
    encrypted: bool = True


class EventSummaryEntry(BaseModel):
    count: int = Field(ge=0)
    total_contribution: int = Field(ge=0)


class IntegrityReport(BaseModel):
    report_id: str
    exam_id: str
    session_id: str
    candidate_id: str
    generated_at: datetime
    exam_duration_minutes: int

    final_risk_score: int = Field(ge=0, le=100)
    risk_classification: RiskClassification

    score_timeline: list[ScoreTimelinePoint] = Field(default_factory=list)
    events: list[ReportEvent] = Field(default_factory=list)
    event_summary: dict[str, EventSummaryEntry] = Field(default_factory=dict)
    evidence_snapshots: list[EvidenceSnapshotRef] = Field(default_factory=list)

    recommendations: Recommendation
    notes: str = ""

    deleted_at: datetime | None = None
    expires_at: datetime | None = None
