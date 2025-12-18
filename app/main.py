from __future__ import annotations

import asyncio

from fastapi import FastAPI

from app.api.routes import reports, sessions
from app.api.deps import get_repo
from app.core.settings import settings
from app.services.retention import periodic_retention_sweep


def create_app() -> FastAPI:
    app = FastAPI(title="Post-Exam Integrity Reporting")

    app.include_router(sessions.router)
    app.include_router(reports.router)

    # Provide routers access to app state for lightweight notifications.
    reports.router._app = app  # type: ignore[attr-defined]

    app.state.notifications = []
    app.state._retention_stop = asyncio.Event()
    app.state._retention_task = None

    @app.on_event("startup")
    async def _startup() -> None:
        if settings.enable_retention_sweep:
            repo = await get_repo()
            app.state._retention_task = asyncio.create_task(
                periodic_retention_sweep(repo, stop_event=app.state._retention_stop)
            )

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        app.state._retention_stop.set()
        task = app.state._retention_task
        if task:
            task.cancel()

    return app


app = create_app()
