from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.services.retention import sweep_expired


def _admin_headers():
    return {"X-Role": "ADMIN", "X-User-Id": "admin-1"}


@pytest.mark.asyncio
async def test_soft_delete_then_hard_delete_after_expiry(client, seeded, repo):
    exam, candidate, session = seeded

    await client.post(
        f"/exams/{exam.exam_id}/sessions/{session.session_id}/generate-report",
        headers=_admin_headers(),
    )
    report_resp = await client.get(
        f"/exams/{exam.exam_id}/sessions/{session.session_id}/report",
        headers=_admin_headers(),
    )
    report_id = report_resp.json()["report_id"]

    d = await client.delete(f"/reports/{report_id}", headers=_admin_headers())
    assert d.status_code == 204

    # Admin can still view deleted reports for audit
    audit = await client.get(
        f"/exams/{exam.exam_id}/sessions/{session.session_id}/report", headers=_admin_headers()
    )
    assert audit.status_code == 200
    assert audit.json()["deleted_at"] is not None

    # Candidate cannot view deleted report
    cand_missing = await client.get(
        f"/exams/{exam.exam_id}/sessions/{session.session_id}/report",
        headers={"X-Role": "CANDIDATE", "X-User-Id": candidate.candidate_id},
    )
    assert cand_missing.status_code == 404

    # force expiry
    now = datetime.now(UTC) + timedelta(days=31)
    deleted = await sweep_expired(repo, now=now)
    assert deleted >= 1

    assert await repo.get_report(report_id) is None
