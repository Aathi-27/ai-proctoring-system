from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models.common import RiskClassification
from app.models.domain import ProctoringEvent
from app.services.scoring import build_score_timeline, classify_risk, final_score_from_events


def test_classify_risk_thresholds():
    assert classify_risk(0) == RiskClassification.LOW
    assert classify_risk(24) == RiskClassification.LOW
    assert classify_risk(25) == RiskClassification.MEDIUM
    assert classify_risk(49) == RiskClassification.MEDIUM
    assert classify_risk(50) == RiskClassification.HIGH
    assert classify_risk(74) == RiskClassification.HIGH
    assert classify_risk(75) == RiskClassification.CRITICAL
    assert classify_risk(100) == RiskClassification.CRITICAL


def test_final_score_clamped():
    events = [
        ProctoringEvent(
            event_id="e1",
            exam_id="x",
            session_id="s",
            candidate_id="c",
            timestamp=datetime.now(UTC),
            type="TAB_SWITCHED",
            confidence=0.8,
            risk_contribution=90,
        ),
        ProctoringEvent(
            event_id="e2",
            exam_id="x",
            session_id="s",
            candidate_id="c",
            timestamp=datetime.now(UTC),
            type="MOBILE_DETECTED",
            confidence=0.9,
            risk_contribution=30,
        ),
    ]
    assert final_score_from_events(events) == 100


def test_score_timeline_5_min_buckets():
    started = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
    ended = datetime(2025, 1, 1, 10, 15, tzinfo=UTC)

    events = [
        ProctoringEvent(
            event_id="e1",
            exam_id="x",
            session_id="s",
            candidate_id="c",
            timestamp=started + timedelta(minutes=1),
            type="TAB_SWITCHED",
            confidence=0.8,
            risk_contribution=10,
        ),
        ProctoringEvent(
            event_id="e2",
            exam_id="x",
            session_id="s",
            candidate_id="c",
            timestamp=started + timedelta(minutes=6),
            type="MOBILE_DETECTED",
            confidence=0.9,
            risk_contribution=20,
        ),
    ]

    timeline = build_score_timeline(
        started_at=started,
        ended_at=ended,
        events=events,
        bucket_minutes=5,
    )

    # points at 10:00, 10:05, 10:10, 10:15
    assert [p.timestamp for p in timeline][:4] == [
        started,
        started + timedelta(minutes=5),
        started + timedelta(minutes=10),
        started + timedelta(minutes=15),
    ]
    assert [p.score for p in timeline][:4] == [10, 30, 30, 30]
