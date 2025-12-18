from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.core.settings import settings
from app.models.domain import EvidenceSnapshot, ProctoringEvent
from app.models.report import EvidenceSnapshotRef, IntegrityReport
from app.repositories.base import Repository
from app.services.scoring import (
    build_event_summary,
    build_score_timeline,
    classify_risk,
    final_score_from_events,
    recommendation_for,
    to_report_events,
)


async def generate_integrity_report(
    *,
    repo: Repository,
    exam_id: str,
    session_id: str,
) -> IntegrityReport:
    session = await repo.get_session(exam_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.ended_at:
        raise HTTPException(status_code=409, detail="Session has not ended")

    exam = await repo.get_exam(exam_id)
    candidate = await repo.get_candidate(session.candidate_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    retention_days = (
        exam.retention_days
        if exam.retention_days is not None
        else settings.default_retention_days
    )

    events: list[ProctoringEvent] = await repo.list_events(exam_id, session_id)
    snapshots: list[EvidenceSnapshot] = await repo.list_snapshots(exam_id, session_id)

    final_score = final_score_from_events(events)
    classification = classify_risk(final_score)

    report = IntegrityReport(
        report_id=str(uuid.uuid4()),
        exam_id=exam_id,
        session_id=session_id,
        candidate_id=session.candidate_id,
        generated_at=datetime.now(UTC),
        exam_duration_minutes=session.duration_minutes() or 0,
        final_risk_score=final_score,
        risk_classification=classification,
        score_timeline=build_score_timeline(
            started_at=session.started_at,
            ended_at=session.ended_at,
            events=events,
            bucket_minutes=5,
        ),
        events=to_report_events(events),
        event_summary=build_event_summary(events),
        evidence_snapshots=[_to_snapshot_ref(s) for s in snapshots],
        recommendations=recommendation_for(classification),
        notes="",
        deleted_at=None,
        expires_at=datetime.now(UTC) + timedelta(days=retention_days),
    )

    await repo.upsert_report(report)
    return report


def _to_snapshot_ref(snapshot: EvidenceSnapshot) -> EvidenceSnapshotRef:
    return EvidenceSnapshotRef(
        snapshot_id=snapshot.snapshot_id,
        timestamp=snapshot.timestamp,
        event_type=snapshot.event_type,
        s3_url=snapshot.s3_url,
        encrypted=snapshot.encrypted,
    )
