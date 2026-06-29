import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from pydantic import ValidationError

logger = logging.getLogger("api.exceptions")

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles deliberately thrown API errors (e.g., 404 Not Found, 400 Bad Request)."""
    req_id = getattr(request.state, "request_id", "unknown")
    
    # Optional: Log 5xx HTTPExceptions as errors, 4xx as warnings
    if exc.status_code >= 500:
        logger.error(f"[{req_id}] HTTP {exc.status_code}: {exc.detail}")
    else:
        logger.warning(f"[{req_id}] HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "http_error",
            "message": exc.detail,
            "request_id": req_id
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles bad inbound payloads from the client (e.g., missing fields, wrong types)."""
    req_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"[{req_id}] Request Validation Failed: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "request_id": req_id
        }
    )

async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Handles internal schema failures (e.g., database returning bad data to a Response model)."""
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{req_id}] Internal Pydantic Schema Error: {exc.errors()}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "schema_validation_error",
            "message": "Internal schema validation failed",
            "request_id": req_id
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    """The ultimate safety net for unhandled crashes (e.g., DB connection dropped, KeyError)."""
    req_id = getattr(request.state, "request_id", "unknown")
    logger.critical(f"[{req_id}] UNHANDLED EXCEPTION: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "request_id": req_id
        }
    )