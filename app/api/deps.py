from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from app.models.common import Role, User
from app.repositories.inmemory import InMemoryRepository


_repo_singleton: InMemoryRepository | None = None


def _get_default_repo() -> InMemoryRepository:
    global _repo_singleton
    if _repo_singleton is None:
        _repo_singleton = InMemoryRepository()
    return _repo_singleton


async def get_repo():
    # Default to in-memory to keep local/dev/test friction low.
    # Production deployments can override this dependency to use MongoRepository.
    return _get_default_repo()


def _parse_monitored_exam_ids(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


async def get_current_user(
    x_role: str | None = Header(default=None, alias="X-Role"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_monitored_exam_ids: str | None = Header(default=None, alias="X-Monitored-Exam-Ids"),
) -> User:
    if not x_role or not x_user_id:
        raise HTTPException(status_code=401, detail="Missing authentication headers")
    try:
        role = Role(x_role)
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid role") from e
    return User(
        user_id=x_user_id,
        role=role,
        monitored_exam_ids=_parse_monitored_exam_ids(x_monitored_exam_ids),
    )


def require_roles(*roles: Role):
    async def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _dep
