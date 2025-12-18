from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.domain import EvidenceSnapshot, ProctoringEvent


def _admin_headers():
    return {"X-Role": "ADMIN", "X-User-Id": "admin-1"}


def _candidate_headers(candidate_id: str):
    return {"X-Role": "CANDIDATE", "X-User-Id": candidate_id}


def _invigilator_headers(invigilator_id: str, exam_ids: list[str]):
    return {
        "X-Role": "INVIGILATOR",
        "X-User-Id": invigilator_id,
        "X-Monitored-Exam-Ids": ",".join(exam_ids),
    }


@pytest.mark.asyncio
async def test_generate_report_endpoint_and_export_pdf(client, seeded, repo):
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
    await repo.insert_snapshot(
        EvidenceSnapshot(
            snapshot_id="s1",
            exam_id=exam.exam_id,
            session_id=session.session_id,
            candidate_id=candidate.candidate_id,
            timestamp=t0 + timedelta(minutes=2),
            event_type="TAB_SWITCHED",
            s3_url="s3://bucket/s1.jpg",
            encrypted=True,
        )
    )

    r = await client.post(
        f"/exams/{exam.exam_id}/sessions/{session.session_id}/generate-report",
        headers=_admin_headers(),
    )
    assert r.status_code == 202

    report_resp = await client.get(
        f"/exams/{exam.exam_id}/sessions/{session.session_id}/report",
        headers=_admin_headers(),
    )
    assert report_resp.status_code == 200
    report_id = report_resp.json()["report_id"]

    pdf = await client.get(
        f"/reports/{report_id}/export?format=pdf",
        headers=_admin_headers(),
    )
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content[:4] == b"%PDF"

    csv = await client.get(
        f"/reports/{report_id}/export?format=csv",
        headers=_admin_headers(),
    )
    assert csv.status_code == 200
    assert csv.headers["content-type"].startswith("text/csv")
    assert b"event_id,timestamp,type,confidence,risk_contribution" in csv.content

    html = await client.get(
        f"/reports/{report_id}/export?format=html",
        headers=_admin_headers(),
    )
    assert html.status_code == 200
    assert html.headers["content-type"].startswith("text/html")
    assert "Recharts" in html.text


@pytest.mark.asyncio
async def test_rbac_candidate_can_only_view_own_report(client, repo):
    # Seed two candidates + sessions + reports
    from app.models.domain import Candidate, Exam, ExamSession

    exam = Exam(exam_id="exam-2", name="Chemistry", retention_days=30)
    cand1 = Candidate(candidate_id="cand-a", name="A")
    cand2 = Candidate(candidate_id="cand-b", name="B")
    await repo.upsert_exam(exam)
    await repo.upsert_candidate(cand1)
    await repo.upsert_candidate(cand2)

    started = datetime.now(UTC) - timedelta(minutes=30)
    ended = datetime.now(UTC)

    s1 = ExamSession(
        session_id="sess-a",
        exam_id=exam.exam_id,
        candidate_id=cand1.candidate_id,
        started_at=started,
        ended_at=ended,
    )
    s2 = ExamSession(
        session_id="sess-b",
        exam_id=exam.exam_id,
        candidate_id=cand2.candidate_id,
        started_at=started,
        ended_at=ended,
    )
    await repo.upsert_session(s1)
    await repo.upsert_session(s2)

    # Generate both reports synchronously via endpoint
    await client.post(
        f"/exams/{exam.exam_id}/sessions/{s1.session_id}/generate-report",
        headers=_admin_headers(),
    )
    await client.post(
        f"/exams/{exam.exam_id}/sessions/{s2.session_id}/generate-report",
        headers=_admin_headers(),
    )

    # Candidate A should access only their session report
    ok = await client.get(
        f"/exams/{exam.exam_id}/sessions/{s1.session_id}/report",
        headers=_candidate_headers(cand1.candidate_id),
    )
    assert ok.status_code == 200

    forbidden = await client.get(
        f"/exams/{exam.exam_id}/sessions/{s2.session_id}/report",
        headers=_candidate_headers(cand1.candidate_id),
    )
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_rbac_invigilator_can_list_only_monitored_exam_reports(client, repo):
    from app.models.domain import Candidate, Exam, ExamSession

    exam1 = Exam(exam_id="exam-a", name="Math", retention_days=30)
    exam2 = Exam(exam_id="exam-b", name="Bio", retention_days=30)
    cand = Candidate(candidate_id="cand-z", name="Z")

    await repo.upsert_exam(exam1)
    await repo.upsert_exam(exam2)
    await repo.upsert_candidate(cand)

    started = datetime.now(UTC) - timedelta(minutes=30)
    ended = datetime.now(UTC)

    s1 = ExamSession(
        session_id="sess-1",
        exam_id=exam1.exam_id,
        candidate_id=cand.candidate_id,
        started_at=started,
        ended_at=ended,
    )
    s2 = ExamSession(
        session_id="sess-2",
        exam_id=exam2.exam_id,
        candidate_id=cand.candidate_id,
        started_at=started,
        ended_at=ended,
    )
    await repo.upsert_session(s1)
    await repo.upsert_session(s2)

    await client.post(
        f"/exams/{exam1.exam_id}/sessions/{s1.session_id}/generate-report",
        headers=_admin_headers(),
    )
    await client.post(
        f"/exams/{exam2.exam_id}/sessions/{s2.session_id}/generate-report",
        headers=_admin_headers(),
    )

    inv_headers = _invigilator_headers("inv-1", [exam1.exam_id])

    ok = await client.get(
        f"/exams/{exam1.exam_id}/reports?page=1&limit=50",
        headers=inv_headers,
    )
    assert ok.status_code == 200
    assert len(ok.json()) == 1

    forbidden = await client.get(
        f"/exams/{exam2.exam_id}/reports?page=1&limit=50",
        headers=inv_headers,
    )
    assert forbidden.status_code == 403
