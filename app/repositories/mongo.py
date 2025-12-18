from __future__ import annotations

from datetime import datetime

from app.models.domain import Candidate, EvidenceSnapshot, Exam, ExamSession, ProctoringEvent
from app.models.report import IntegrityReport


class MongoRepository:
    def __init__(self, db):
        self._db = db

    async def upsert_exam(self, exam: Exam) -> None:
        await self._db.exams.update_one(
            {"exam_id": exam.exam_id},
            {"$set": exam.model_dump()},
            upsert=True,
        )

    async def get_exam(self, exam_id: str) -> Exam | None:
        doc = await self._db.exams.find_one({"exam_id": exam_id})
        return Exam.model_validate(doc) if doc else None

    async def upsert_candidate(self, candidate: Candidate) -> None:
        await self._db.candidates.update_one(
            {"candidate_id": candidate.candidate_id},
            {"$set": candidate.model_dump()},
            upsert=True,
        )

    async def get_candidate(self, candidate_id: str) -> Candidate | None:
        doc = await self._db.candidates.find_one({"candidate_id": candidate_id})
        return Candidate.model_validate(doc) if doc else None

    async def upsert_session(self, session: ExamSession) -> None:
        await self._db.sessions.update_one(
            {"exam_id": session.exam_id, "session_id": session.session_id},
            {"$set": session.model_dump()},
            upsert=True,
        )

    async def get_session(self, exam_id: str, session_id: str) -> ExamSession | None:
        doc = await self._db.sessions.find_one({"exam_id": exam_id, "session_id": session_id})
        return ExamSession.model_validate(doc) if doc else None

    async def list_events(self, exam_id: str, session_id: str) -> list[ProctoringEvent]:
        cursor = self._db.events.find({"exam_id": exam_id, "session_id": session_id}).sort(
            "timestamp", 1
        )
        docs = await cursor.to_list(length=None)
        return [ProctoringEvent.model_validate(d) for d in docs]

    async def insert_event(self, event: ProctoringEvent) -> None:
        await self._db.events.insert_one(event.model_dump())

    async def list_snapshots(self, exam_id: str, session_id: str) -> list[EvidenceSnapshot]:
        cursor = self._db.snapshots.find({"exam_id": exam_id, "session_id": session_id}).sort(
            "timestamp", 1
        )
        docs = await cursor.to_list(length=None)
        return [EvidenceSnapshot.model_validate(d) for d in docs]

    async def insert_snapshot(self, snapshot: EvidenceSnapshot) -> None:
        await self._db.snapshots.insert_one(snapshot.model_dump())

    async def upsert_report(self, report: IntegrityReport) -> None:
        await self._db.reports.update_one(
            {"exam_id": report.exam_id, "session_id": report.session_id},
            {"$set": report.model_dump()},
            upsert=True,
        )

    async def get_report_by_session(self, exam_id: str, session_id: str) -> IntegrityReport | None:
        doc = await self._db.reports.find_one(
            {"exam_id": exam_id, "session_id": session_id, "deleted_at": None}
        )
        return IntegrityReport.model_validate(doc) if doc else None

    async def get_report(self, report_id: str) -> IntegrityReport | None:
        doc = await self._db.reports.find_one({"report_id": report_id})
        return IntegrityReport.model_validate(doc) if doc else None

    async def list_reports_for_exam(
        self,
        exam_id: str,
        *,
        page: int,
        limit: int,
        include_deleted: bool,
    ) -> list[IntegrityReport]:
        query = {"exam_id": exam_id}
        if not include_deleted:
            query["deleted_at"] = None
        cursor = (
            self._db.reports.find(query)
            .sort("generated_at", -1)
            .skip(max(0, (page - 1) * limit))
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [IntegrityReport.model_validate(d) for d in docs]

    async def soft_delete_report(
        self,
        report_id: str,
        *,
        deleted_at: datetime,
        expires_at: datetime,
    ) -> bool:
        result = await self._db.reports.update_one(
            {"report_id": report_id},
            {"$set": {"deleted_at": deleted_at, "expires_at": expires_at}},
        )
        return result.matched_count == 1

    async def hard_delete_report(self, report_id: str) -> bool:
        report = await self.get_report(report_id)
        if not report:
            return False
        await self._db.reports.delete_one({"report_id": report_id})
        await self._db.events.delete_many(
            {"exam_id": report.exam_id, "session_id": report.session_id}
        )
        await self._db.snapshots.delete_many(
            {"exam_id": report.exam_id, "session_id": report.session_id}
        )
        return True

    async def hard_delete_expired(self, *, now: datetime) -> int:
        cursor = self._db.reports.find({"expires_at": {"$lte": now}})
        docs = await cursor.to_list(length=None)
        deleted = 0
        for doc in docs:
            report = IntegrityReport.model_validate(doc)
            if await self.hard_delete_report(report.report_id):
                deleted += 1
        return deleted
