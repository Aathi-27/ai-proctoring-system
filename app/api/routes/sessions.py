from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_repo, require_roles
from app.models.common import Role
from app.models.domain import Candidate, EvidenceSnapshot, Exam, ExamSession, ProctoringEvent
from app.repositories.base import Repository
from app.services.report_generation import generate_integrity_report

router = APIRouter(tags=["sessions"])


@router.post("/exams", response_model=Exam)
async def upsert_exam(
    exam: Exam,
    repo: Repository = Depends(get_repo),
    _=Depends(require_roles(Role.ADMIN)),
):
    await repo.upsert_exam(exam)
    return exam


@router.post("/candidates", response_model=Candidate)
async def upsert_candidate(
    candidate: Candidate,
    repo: Repository = Depends(get_repo),
    _=Depends(require_roles(Role.ADMIN)),
):
    await repo.upsert_candidate(candidate)
    return candidate


@router.post("/exams/{exam_id}/sessions", response_model=ExamSession)
async def create_session(
    exam_id: str,
    candidate_id: str,
    repo: Repository = Depends(get_repo),
    _=Depends(require_roles(Role.ADMIN)),
):
    if not await repo.get_exam(exam_id):
        raise HTTPException(status_code=404, detail="Exam not found")
    if not await repo.get_candidate(candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found")

    session = ExamSession(
        session_id=str(uuid.uuid4()),
        exam_id=exam_id,
        candidate_id=candidate_id,
        started_at=datetime.now(UTC),
        ended_at=None,
    )
    await repo.upsert_session(session)
    return session


@router.post("/exams/{exam_id}/sessions/{session_id}/end", status_code=202)
async def end_session(
    exam_id: str,
    session_id: str,
    background_tasks: BackgroundTasks,
    repo: Repository = Depends(get_repo),
    _=Depends(require_roles(Role.ADMIN)),
):
    session = await repo.get_session(exam_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.ended_at:
        return {"status": "already_ended"}

    session.ended_at = datetime.now(UTC)
    await repo.upsert_session(session)

    async def _job() -> None:
        await generate_integrity_report(repo=repo, exam_id=exam_id, session_id=session_id)

    background_tasks.add_task(_job)
    return {"status": "ended", "report_generation": "queued"}


@router.post("/exams/{exam_id}/sessions/{session_id}/events", response_model=ProctoringEvent)
async def add_event(
    exam_id: str,
    session_id: str,
    payload: ProctoringEvent,
    repo: Repository = Depends(get_repo),
    _=Depends(require_roles(Role.ADMIN)),
):
    session = await repo.get_session(exam_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await repo.insert_event(payload)
    return payload


@router.post("/exams/{exam_id}/sessions/{session_id}/snapshots", response_model=EvidenceSnapshot)
async def add_snapshot(
    exam_id: str,
    session_id: str,
    payload: EvidenceSnapshot,
    repo: Repository = Depends(get_repo),
    _=Depends(require_roles(Role.ADMIN)),
):
    session = await repo.get_session(exam_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await repo.insert_snapshot(payload)
    return payload
