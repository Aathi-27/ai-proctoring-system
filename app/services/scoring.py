from __future__ import annotations

from datetime import datetime, timedelta

from app.models.common import Recommendation, RiskClassification
from app.models.domain import ProctoringEvent
from app.models.report import EventSummaryEntry, ReportEvent, ScoreTimelinePoint


def clamp_score(score: int) -> int:
    return max(0, min(100, int(score)))


def classify_risk(score: int) -> RiskClassification:
    score = clamp_score(score)
    if score >= 75:
        return RiskClassification.CRITICAL
    if score >= 50:
        return RiskClassification.HIGH
    if score >= 25:
        return RiskClassification.MEDIUM
    return RiskClassification.LOW


def recommendation_for(classification: RiskClassification) -> Recommendation:
    if classification in {RiskClassification.HIGH, RiskClassification.CRITICAL}:
        return Recommendation.FLAG_FOR_REVIEW
    if classification == RiskClassification.MEDIUM:
        return Recommendation.REVIEW
    return Recommendation.PASS


def build_event_summary(events: list[ProctoringEvent]) -> dict[str, EventSummaryEntry]:
    summary: dict[str, EventSummaryEntry] = {}
    for e in events:
        entry = summary.get(e.type)
        if not entry:
            summary[e.type] = EventSummaryEntry(count=1, total_contribution=e.risk_contribution)
        else:
            entry.count += 1
            entry.total_contribution += e.risk_contribution
            summary[e.type] = entry
    return summary


def final_score_from_events(events: list[ProctoringEvent]) -> int:
    return clamp_score(sum(e.risk_contribution for e in events))


def build_score_timeline(
    *,
    started_at: datetime,
    ended_at: datetime,
    events: list[ProctoringEvent],
    bucket_minutes: int = 5,
) -> list[ScoreTimelinePoint]:
    if ended_at < started_at:
        ended_at = started_at

    sorted_events = sorted(events, key=lambda e: e.timestamp)
    buckets: list[ScoreTimelinePoint] = []

    bucket = started_at
    idx = 0
    running = 0

    while bucket <= ended_at:
        bucket_end = bucket + timedelta(minutes=bucket_minutes)
        while idx < len(sorted_events) and sorted_events[idx].timestamp < bucket_end:
            running += sorted_events[idx].risk_contribution
            idx += 1
        buckets.append(ScoreTimelinePoint(timestamp=bucket, score=clamp_score(running)))
        bucket = bucket_end

    if not buckets or buckets[-1].timestamp != ended_at:
        # Ensure a final point exactly at end time for rendering stability.
        while idx < len(sorted_events) and sorted_events[idx].timestamp <= ended_at:
            running += sorted_events[idx].risk_contribution
            idx += 1
        buckets.append(ScoreTimelinePoint(timestamp=ended_at, score=clamp_score(running)))

    return buckets


def to_report_events(events: list[ProctoringEvent]) -> list[ReportEvent]:
    return [
        ReportEvent(
            event_id=e.event_id,
            timestamp=e.timestamp,
            type=e.type,
            confidence=e.confidence,
            risk_contribution=e.risk_contribution,
        )
        for e in sorted(events, key=lambda e: e.timestamp)
    ]
