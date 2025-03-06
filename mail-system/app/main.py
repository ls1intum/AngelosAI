import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.logging_config import setup_logging
from app.managers.thread_manager import ThreadManager
from app.routers.mail_router import router as mail_router

setup_logging()
thread_manager = ThreadManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("FastAPI application startup...")
    yield
    logging.info("FastAPI application shutting down...")
    thread_manager.stop_all()


app = FastAPI(lifespan=lifespan)
app.include_router(mail_router, prefix="/api/mail", tags=["mail"])
