from __future__ import annotations

import copy
from datetime import datetime

from app.models.domain import Candidate, EvidenceSnapshot, Exam, ExamSession, ProctoringEvent
from app.models.report import IntegrityReport


class InMemoryRepository:
    def __init__(self) -> None:
        self.exams: dict[str, Exam] = {}
        self.candidates: dict[str, Candidate] = {}
        self.sessions: dict[tuple[str, str], ExamSession] = {}
        self.events: dict[tuple[str, str], list[ProctoringEvent]] = {}
        self.snapshots: dict[tuple[str, str], list[EvidenceSnapshot]] = {}
        self.reports_by_id: dict[str, IntegrityReport] = {}
        self.report_id_by_session: dict[tuple[str, str], str] = {}

    async def upsert_exam(self, exam: Exam) -> None:
        self.exams[exam.exam_id] = exam

    async def get_exam(self, exam_id: str) -> Exam | None:
        exam = self.exams.get(exam_id)
        return copy.deepcopy(exam) if exam else None

    async def upsert_candidate(self, candidate: Candidate) -> None:
        self.candidates[candidate.candidate_id] = candidate

    async def get_candidate(self, candidate_id: str) -> Candidate | None:
        candidate = self.candidates.get(candidate_id)
        return copy.deepcopy(candidate) if candidate else None

    async def upsert_session(self, session: ExamSession) -> None:
        self.sessions[(session.exam_id, session.session_id)] = session

    async def get_session(self, exam_id: str, session_id: str) -> ExamSession | None:
        session = self.sessions.get((exam_id, session_id))
        return copy.deepcopy(session) if session else None

    async def list_events(self, exam_id: str, session_id: str) -> list[ProctoringEvent]:
        items = self.events.get((exam_id, session_id), [])
        return copy.deepcopy(sorted(items, key=lambda e: e.timestamp))

    async def insert_event(self, event: ProctoringEvent) -> None:
        key = (event.exam_id, event.session_id)
        self.events.setdefault(key, []).append(event)

    async def list_snapshots(self, exam_id: str, session_id: str) -> list[EvidenceSnapshot]:
        items = self.snapshots.get((exam_id, session_id), [])
        return copy.deepcopy(sorted(items, key=lambda s: s.timestamp))

    async def insert_snapshot(self, snapshot: EvidenceSnapshot) -> None:
        key = (snapshot.exam_id, snapshot.session_id)
        self.snapshots.setdefault(key, []).append(snapshot)

    async def upsert_report(self, report: IntegrityReport) -> None:
        existing_id = self.report_id_by_session.get((report.exam_id, report.session_id))
        if existing_id and existing_id != report.report_id:
            self.reports_by_id.pop(existing_id, None)
        self.reports_by_id[report.report_id] = report
        self.report_id_by_session[(report.exam_id, report.session_id)] = report.report_id

    async def get_report_by_session(self, exam_id: str, session_id: str) -> IntegrityReport | None:
        report_id = self.report_id_by_session.get((exam_id, session_id))
        if not report_id:
            return None
        report = self.reports_by_id.get(report_id)
        return copy.deepcopy(report) if report else None

    async def get_report(self, report_id: str) -> IntegrityReport | None:
        report = self.reports_by_id.get(report_id)
        return copy.deepcopy(report) if report else None

    async def list_reports_for_exam(
        self,
        exam_id: str,
        *,
        page: int,
        limit: int,
        include_deleted: bool,
    ) -> list[IntegrityReport]:
        items = [r for r in self.reports_by_id.values() if r.exam_id == exam_id]
        if not include_deleted:
            items = [r for r in items if r.deleted_at is None]
        items.sort(key=lambda r: r.generated_at, reverse=True)
        start = max(0, (page - 1) * limit)
        end = start + limit
        return copy.deepcopy(items[start:end])

    async def soft_delete_report(
        self,
        report_id: str,
        *,
        deleted_at: datetime,
        expires_at: datetime,
    ) -> bool:
        report = self.reports_by_id.get(report_id)
        if not report:
            return False
        report.deleted_at = deleted_at
        report.expires_at = expires_at
        self.reports_by_id[report_id] = report
        return True

    async def hard_delete_report(self, report_id: str) -> bool:
        report = self.reports_by_id.pop(report_id, None)
        if not report:
            return False
        self.report_id_by_session.pop((report.exam_id, report.session_id), None)

        # Evidence is retained in a separate collection in real deployments.
        # For in-memory repo, remove only items associated with the session.
        self.snapshots.pop((report.exam_id, report.session_id), None)
        self.events.pop((report.exam_id, report.session_id), None)
        return True

    async def hard_delete_expired(self, *, now: datetime) -> int:
        expired = [
            r.report_id
            for r in self.reports_by_id.values()
            if r.expires_at and r.expires_at <= now
        ]
        deleted = 0
        for report_id in expired:
            if await self.hard_delete_report(report_id):
                deleted += 1
        return deleted
