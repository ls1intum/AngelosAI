import logging

from fastapi import HTTPException, APIRouter, status, Response, Depends

from app.managers.auth_handler import LoginRequest
from app.utils.dependencies import auth_handler
from app.utils.environment import config

auth_router = APIRouter(prefix="/api", tags=["authorization"], dependencies=[Depends(auth_handler.verify_api_key)])

@auth_router.post("/token")
async def login(login_request: LoginRequest):
    if config.WITHOUT_USER_LOGIN == "true" or (
            login_request.username == config.EXPECTED_USERNAME and login_request.password == config.EXPECTED_PASSWORD):
        token_data = {"sub": "angular_app"}
        access_token = auth_handler.create_access_token(data=token_data)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")