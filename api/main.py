import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from api.config import api_settings
from api.dependencies import get_container
from api.middleware.request_id import RequestIDMiddleware
from api.middleware.timing import TimingMiddleware
from api.middleware.request_logger import RequestLoggerMiddleware
from api.exceptions.handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    pydantic_validation_handler
)
from api.routers import (
    v1_system,
    v1_tickets,
    v1_reviews,
    v1_crm,
    v1_translations,
    v1_proactive,
    v1_analytics
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("enterprise_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes expensive dependencies once on startup."""
    logger.info(" Starting Enterprise CRM Platform API...")
    try:
        get_container()
        logger.info(" Dependency Container Initialized")
    except Exception as e:
        logger.exception(" Failed to initialize Dependency Container")
        raise e

    yield

    logger.info(" Shutting down Enterprise CRM Platform API gracefully...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=api_settings.API_TITLE,
        version=api_settings.API_VERSION,
        description="Enterprise CRM & Multi-Agent Orchestration Platform",
        lifespan=lifespan,
        contact={
            "name": "Platform Engineering",
            "email": "support@your-enterprise.com"
        },
        license_info={
            "name": "Internal Enterprise Use Only"
        },
        docs_url="/docs",
        redoc_url="/redoc",
    )


    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.add_middleware(TimingMiddleware)

    app.add_middleware(RequestLoggerMiddleware)

    app.add_middleware(RequestIDMiddleware)


    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_handler)
    app.add_exception_handler(Exception, global_exception_handler)


    @app.get("/health", tags=["System"], summary="Load Balancer Health Check")
    def health():
        """Lightweight root probe for AWS Target Groups and Kubernetes."""
        return {
            "status": "healthy",
            "version": api_settings.API_VERSION,
            "environment": api_settings.ENVIRONMENT 
        }

    app.include_router(v1_system.router)
    app.include_router(v1_tickets.router)
    app.include_router(v1_reviews.router)
    app.include_router(v1_crm.router)
    app.include_router(v1_translations.router)
    app.include_router(v1_proactive.router)
    app.include_router(v1_analytics.router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)