from fastapi import FastAPI

from core.lifespan import lifespan
from core.settings import settings
from v1 import api as v1_api


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app.title,
        version=settings.app.version,
        description=settings.app.description,
        contact=settings.app.contact.model_dump(),
        lifespan=lifespan,
    )
    app.include_router(v1_api.router, prefix="/api/v1")
    return app


app = create_app()
