from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.core.settings import settings
from app.repositories.base import Repository


async def sweep_expired(repo: Repository, *, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    return await repo.hard_delete_expired(now=now)


async def periodic_retention_sweep(repo: Repository, *, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await sweep_expired(repo)
        finally:
            try:
                await asyncio.wait_for(
                    stop_event.wait(), timeout=settings.retention_sweep_interval_seconds
                )
            except TimeoutError:
                pass
