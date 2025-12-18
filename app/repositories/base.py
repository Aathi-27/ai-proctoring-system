from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.models.domain import (
    Candidate,
    EvidenceSnapshot,
    Exam,
    ExamSession,
    ProctoringEvent,
)
from app.models.report import IntegrityReport


class Repository(Protocol):
    async def upsert_exam(self, exam: Exam) -> None: ...

    async def get_exam(self, exam_id: str) -> Exam | None: ...

    async def upsert_candidate(self, candidate: Candidate) -> None: ...

    async def get_candidate(self, candidate_id: str) -> Candidate | None: ...

    async def upsert_session(self, session: ExamSession) -> None: ...

    async def get_session(self, exam_id: str, session_id: str) -> ExamSession | None: ...

    async def list_events(self, exam_id: str, session_id: str) -> list[ProctoringEvent]: ...

    async def insert_event(self, event: ProctoringEvent) -> None: ...

    async def list_snapshots(
        self, exam_id: str, session_id: str
    ) -> list[EvidenceSnapshot]: ...

    async def insert_snapshot(self, snapshot: EvidenceSnapshot) -> None: ...

    async def upsert_report(self, report: IntegrityReport) -> None: ...

    async def get_report_by_session(
        self, exam_id: str, session_id: str
    ) -> IntegrityReport | None: ...

    async def get_report(self, report_id: str) -> IntegrityReport | None: ...

    async def list_reports_for_exam(
        self,
        exam_id: str,
        *,
        page: int,
        limit: int,
        include_deleted: bool,
    ) -> list[IntegrityReport]: ...

    async def soft_delete_report(
        self,
        report_id: str,
        *,
        deleted_at: datetime,
        expires_at: datetime,
    ) -> bool: ...

    async def hard_delete_report(self, report_id: str) -> bool: ...

    async def hard_delete_expired(self, *, now: datetime) -> int: ...
