from __future__ import annotations

import csv
import io
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse

from app.api.deps import get_current_user, get_repo, require_roles
from app.core.settings import settings
from app.models.common import Role, User
from app.models.report import IntegrityReport
from app.repositories.base import Repository
from app.services.report_generation import generate_integrity_report
from app.services.report_rendering import render_report_html, render_report_pdf

router = APIRouter(tags=["reports"])


def _assert_exam_access(user: User, exam_id: str) -> None:
    if user.role == Role.ADMIN:
        return
    if user.role == Role.INVIGILATOR and exam_id in user.monitored_exam_ids:
        return
    raise HTTPException(status_code=403, detail="Forbidden")


def _assert_report_access(user: User, report: IntegrityReport, exam_id: str) -> None:
    if user.role == Role.ADMIN:
        return
    if user.role == Role.CANDIDATE:
        if report.candidate_id != user.user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return
    if user.role == Role.INVIGILATOR:
        if exam_id not in user.monitored_exam_ids:
            raise HTTPException(status_code=403, detail="Forbidden")
        return
    raise HTTPException(status_code=403, detail="Forbidden")


@router.post(
    "/exams/{exam_id}/sessions/{session_id}/generate-report",
    status_code=202,
)
async def generate_report(
    exam_id: str,
    session_id: str,
    background_tasks: BackgroundTasks,
    repo: Repository = Depends(get_repo),
    user: User = Depends(require_roles(Role.ADMIN, Role.INVIGILATOR)),
):
    _assert_exam_access(user, exam_id)

    existing = await repo.get_report_by_session(exam_id, session_id)
    if existing and existing.deleted_at is None:
        return {"status": "already_generated", "report_id": existing.report_id}

    async def _job() -> None:
        report = await generate_integrity_report(repo=repo, exam_id=exam_id, session_id=session_id)
        # Lightweight admin notification (in-memory) to support dashboard polling.
        if hasattr(router, "_app"):
            app = getattr(router, "_app")
            app.state.notifications.append(
                {
                    "type": "REPORT_GENERATED",
                    "report_id": report.report_id,
                    "exam_id": exam_id,
                    "session_id": session_id,
                    "generated_at": report.generated_at.isoformat(),
                }
            )

    background_tasks.add_task(_job)
    return {"status": "queued"}


@router.get("/exams/{exam_id}/sessions/{session_id}/report", response_model=IntegrityReport)
async def get_report_for_session(
    exam_id: str,
    session_id: str,
    repo: Repository = Depends(get_repo),
    user: User = Depends(get_current_user),
):
    report = await repo.get_report_by_session(exam_id, session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.deleted_at is not None and user.role != Role.ADMIN:
        raise HTTPException(status_code=404, detail="Report not found")
    _assert_report_access(user, report, exam_id)
    return report


@router.get("/exams/{exam_id}/reports", response_model=list[IntegrityReport])
async def list_reports(
    exam_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    repo: Repository = Depends(get_repo),
    user: User = Depends(get_current_user),
):
    include_deleted = user.role == Role.ADMIN

    if user.role in {Role.ADMIN, Role.INVIGILATOR}:
        _assert_exam_access(user, exam_id)
        reports = await repo.list_reports_for_exam(
            exam_id, page=page, limit=limit, include_deleted=include_deleted
        )
    elif user.role == Role.CANDIDATE:
        reports = await repo.list_reports_for_exam(
            exam_id, page=page, limit=limit, include_deleted=False
        )
        reports = [r for r in reports if r.candidate_id == user.user_id]
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

    return reports


@router.get("/reports/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = Query(default="pdf", pattern="^(pdf|json|csv|html)$"),
    repo: Repository = Depends(get_repo),
    user: User = Depends(get_current_user),
):
    report = await repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.deleted_at is not None and user.role != Role.ADMIN:
        raise HTTPException(status_code=404, detail="Report not found")
    _assert_report_access(user, report, report.exam_id)

    if format == "json":
        return JSONResponse(report.model_dump(mode="json"))

    if format == "csv":
        csv_bytes = _events_csv(report)
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=events-{report_id}.csv"},
        )

    exam = await repo.get_exam(report.exam_id)
    session = await repo.get_session(report.exam_id, report.session_id)
    candidate = await repo.get_candidate(report.candidate_id)
    if not exam or not session or not candidate:
        raise HTTPException(status_code=500, detail="Missing report context")

    if format == "html":
        html = render_report_html(report=report, exam=exam, candidate=candidate, session=session)
        return HTMLResponse(html)

    pdf = render_report_pdf(report=report, exam=exam, candidate=candidate, session=session)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report-{report_id}.pdf"},
    )


@router.delete("/reports/{report_id}", status_code=204)
async def delete_report(
    report_id: str,
    repo: Repository = Depends(get_repo),
    user: User = Depends(require_roles(Role.ADMIN)),
):
    report = await repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    exam = await repo.get_exam(report.exam_id)
    retention_days = (
        exam.retention_days
        if exam and exam.retention_days is not None
        else settings.default_retention_days
    )

    now = datetime.now(UTC)
    expires_at = now + timedelta(days=retention_days)
    ok = await repo.soft_delete_report(report_id, deleted_at=now, expires_at=expires_at)
    if not ok:
        raise HTTPException(status_code=404, detail="Report not found")
    return Response(status_code=204)


@router.get("/admin/notifications")
async def list_notifications(user: User = Depends(require_roles(Role.ADMIN))):
    if not hasattr(router, "_app"):
        return []
    return list(getattr(router, "_app").state.notifications)


def _events_csv(report: IntegrityReport) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["event_id", "timestamp", "type", "confidence", "risk_contribution"])
    for e in report.events:
        writer.writerow(
            [
                e.event_id,
                e.timestamp.isoformat(),
                e.type,
                e.confidence,
                e.risk_contribution,
            ]
        )
    return buf.getvalue().encode("utf-8")
