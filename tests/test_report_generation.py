from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.domain import EvidenceSnapshot, ProctoringEvent
from app.services.report_generation import generate_integrity_report


@pytest.mark.asyncio
async def test_generate_report_from_mock_data(seeded, repo):
    exam, candidate, session = seeded

    t0 = session.started_at
    await repo.insert_event(
        ProctoringEvent(
            event_id="e1",
            exam_id=exam.exam_id,
            session_id=session.session_id,
            candidate_id=candidate.candidate_id,
            timestamp=t0 + timedelta(minutes=1),
            type="TAB_SWITCHED",
            confidence=0.8,
            risk_contribution=10,
        )
    )
    await repo.insert_event(
        ProctoringEvent(
            event_id="e2",
            exam_id=exam.exam_id,
            session_id=session.session_id,
            candidate_id=candidate.candidate_id,
            timestamp=t0 + timedelta(minutes=7),
            type="MOBILE_DETECTED",
            confidence=0.95,
            risk_contribution=60,
        )
    )

    await repo.insert_snapshot(
        EvidenceSnapshot(
            snapshot_id="s1",
            exam_id=exam.exam_id,
            session_id=session.session_id,
            candidate_id=candidate.candidate_id,
            timestamp=t0 + timedelta(minutes=7),
            event_type="MOBILE_DETECTED",
            s3_url="s3://bucket/s1.jpg",
            encrypted=True,
        )
    )

    report = await generate_integrity_report(
        repo=repo,
        exam_id=exam.exam_id,
        session_id=session.session_id,
    )

    assert report.exam_id == exam.exam_id
    assert report.session_id == session.session_id
    assert report.candidate_id == candidate.candidate_id
    assert report.exam_duration_minutes >= 0

    assert report.final_risk_score == 70
    assert report.risk_classification.value == "HIGH"

    assert len(report.events) == 2
    assert report.event_summary["TAB_SWITCHED"].count == 1
    assert report.event_summary["TAB_SWITCHED"].total_contribution == 10
    assert report.event_summary["MOBILE_DETECTED"].total_contribution == 60

    assert len(report.evidence_snapshots) == 1
    assert report.evidence_snapshots[0].s3_url.startswith("s3://")

    # persisted
    stored = await repo.get_report(report.report_id)
    assert stored is not None
    assert stored.report_id == report.report_id


@pytest.mark.asyncio
async def test_generate_report_requires_ended_session(repo):
    from fastapi import HTTPException

    from app.models.domain import Candidate, Exam, ExamSession

    exam_id = "exam-x"
    candidate_id = "cand-x"

    await repo.upsert_exam(Exam(exam_id=exam_id, name="X", retention_days=30))
    await repo.upsert_candidate(Candidate(candidate_id=candidate_id, name="Y"))

    session = ExamSession(
        session_id="sess-x",
        exam_id=exam_id,
        candidate_id=candidate_id,
        started_at=datetime.now(UTC),
        ended_at=None,
    )
    await repo.upsert_session(session)

    with pytest.raises(HTTPException) as exc:
        await generate_integrity_report(repo=repo, exam_id=exam_id, session_id=session.session_id)

    assert exc.value.status_code == 409
