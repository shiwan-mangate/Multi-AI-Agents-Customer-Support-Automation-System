from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from main import main
from model import UnifiedTicket, RequestModel
from logger import logger

import time

app = FastAPI()


@app.post("/webhook", response_model=UnifiedTicket)
def webhook(data: RequestModel):

    try:

        payload = data.model_dump()

        logger.info(
            f"Received request: {payload}"
        )

        result = main(payload)

        logger.info(
            f"Response generated: {result}"
        )

        return result

    except ValueError as ve:

        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )

    except Exception:

        logger.exception(
            "Unhandled application error"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next
):

    start_time = time.time()

    body = await request.body()

    logger.info(
        f"Incoming request: "
        f"{request.method} "
        f"{request.url.path}"
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"Completed "
        f"{request.method} "
        f"{request.url.path} "
        f"in {process_time:.4f}s "
        f"status={response.status_code}"
    )

    return response


@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc
):

    logger.error(
        f"Validation error: "
        f"{exc.errors()}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors()
        }
    )