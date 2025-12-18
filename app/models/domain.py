from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Exam(BaseModel):
    exam_id: str
    name: str
    retention_days: int | None = None


class Candidate(BaseModel):
    candidate_id: str
    name: str


class ExamSession(BaseModel):
    session_id: str
    exam_id: str
    candidate_id: str
    started_at: datetime
    ended_at: datetime | None = None

    def duration_minutes(self) -> int | None:
        if not self.ended_at:
            return None
        seconds = (self.ended_at - self.started_at).total_seconds()
        return max(0, int(round(seconds / 60)))


class ProctoringEvent(BaseModel):
    event_id: str
    exam_id: str
    session_id: str
    candidate_id: str
    timestamp: datetime
    type: str
    confidence: float = Field(ge=0, le=1)
    risk_contribution: int = Field(ge=0)


class EvidenceSnapshot(BaseModel):
    snapshot_id: str
    exam_id: str
    session_id: str
    candidate_id: str
    timestamp: datetime
    event_type: str
    s3_url: str
    encrypted: bool = True
