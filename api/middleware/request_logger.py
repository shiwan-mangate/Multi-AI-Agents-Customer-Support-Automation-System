import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("api.access")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Logs the start and completion of every HTTP request, tying it to the Request ID.
    """
    async def dispatch(self, request: Request, call_next):
        req_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        path = request.url.path
        
        logger.info(f"[{req_id}] -> {method} {path}")
        
        response = await call_next(request)
        
        process_time = getattr(request.state, "process_time", 0.0)
        status = response.status_code
        
        logger.info(f"[{req_id}] <- {method} {path} | Status: {status} | Time: {process_time:.4f}s")
        
        return response