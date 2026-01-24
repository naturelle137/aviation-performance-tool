"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import aircraft, calculations, health, weather

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup: Create database tables (development only)
    if settings.is_development:
        Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Cleanup if needed


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.app_name,
        description="API for calculating aircraft Mass & Balance, fuel planning, and performance",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(aircraft.router, prefix="/api/v1/aircraft", tags=["Aircraft"])
    app.include_router(
        calculations.router, prefix="/api/v1/calculations", tags=["Calculations"]
    )
    app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])

    return app


app = create_app()
