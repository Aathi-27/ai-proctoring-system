from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_repo
from app.main import create_app
from app.models.domain import Candidate, Exam, ExamSession
from app.repositories.inmemory import InMemoryRepository


@pytest.fixture()
def repo() -> InMemoryRepository:
    return InMemoryRepository()


@pytest.fixture()
def app(repo: InMemoryRepository):
    app = create_app()

    async def _get_repo_override():
        return repo

    app.dependency_overrides[get_repo] = _get_repo_override
    return app


@pytest.fixture()
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture()
async def seeded(repo: InMemoryRepository):
    exam = Exam(exam_id="exam-1", name="Physics 101", retention_days=30)
    candidate = Candidate(candidate_id="cand-1", name="Ada Lovelace")

    started_at = datetime.now(UTC) - timedelta(minutes=60)
    ended_at = datetime.now(UTC)
    session = ExamSession(
        session_id="sess-1",
        exam_id=exam.exam_id,
        candidate_id=candidate.candidate_id,
        started_at=started_at,
        ended_at=ended_at,
    )

    await repo.upsert_exam(exam)
    await repo.upsert_candidate(candidate)
    await repo.upsert_session(session)

    return exam, candidate, session
