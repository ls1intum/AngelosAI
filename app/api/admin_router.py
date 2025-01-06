import logging

from fastapi import APIRouter, Depends

from app.utils.dependencies import auth_handler, model
from app.utils.environment import config


admin_router = APIRouter(prefix="/api/admin", tags=["settings", "admin"],
                         dependencies=[Depends(auth_handler.verify_token)])

@admin_router.get("/ping")
async def ping():
    logging.info(config.GPU_URL)
    return {"answer": "Server running."}


@admin_router.get("/hi")
async def ping():
    logging.info("hi")
    return model.complete([{"role": "user", "content": "Hi"}])