import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Calculates total server processing time and attaches it
    to both the response headers and request state.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        request.state.process_time = process_time

        response.headers["X-Process-Time"] = f"{process_time:.4f} sec"

        return response