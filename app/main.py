import logging
import uvicorn

from app.utils.setup_logging import setup_logging

setup_logging()

from app.api.question_router import question_router
from app.api.admin_router import admin_router
from app.api.knowledge_router import knowledge_router

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.responses import JSONResponse

from app.utils.dependencies import shutdown_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up the application...")
    yield
    logging.info("Shutting down models and closing sessions.")
    shutdown_model()


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9007", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


app.include_router(router=question_router)
app.include_router(router=admin_router)
app.include_router(router=knowledge_router)

if __name__ == "__main__":
    logging.info("Starting FastAPI server")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
