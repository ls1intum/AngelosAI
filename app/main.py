import logging

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.responses import JSONResponse

from app.api.question_router import router as question_router
from app.utils.dependencies import shutdown_model
from app.utils.setup_logging import setup_logging

setup_logging()
logging.info("Starting application...")
app = FastAPI(default_response_class=ORJSONResponse)


@app.on_event("shutdown")
async def shutdown_event():
    """Close the model session when the app shuts down"""
    logging.info("Shutting down models and closing sessions.")
    shutdown_model()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


app.include_router(router=question_router)

if __name__ == "__main__":
    logging.info("Starting fast api")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
