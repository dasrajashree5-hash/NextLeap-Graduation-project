"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import router as api_router
from app.config import get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging, new_request_id, request_id_ctx


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Blinkit Discovery Engine",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=settings.cors_origin_regex or None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or new_request_id()
        token = request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_ctx.reset(token)

    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    async def root():
        return {"service": "blinkit-discovery-engine", "docs": "/docs"}

    prefix = settings.api_prefix.rstrip("/")

    @app.get("/themes", include_in_schema=False)
    async def legacy_themes():
        return RedirectResponse(url=f"{prefix}/themes", status_code=307)

    @app.get("/insights", include_in_schema=False)
    async def legacy_insights(request: Request):
        target = f"{prefix}/insights"
        if request.url.query:
            target = f"{target}?{request.url.query}"
        return RedirectResponse(url=target, status_code=307)

    return app


app = create_app()
