import logging
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException, Header
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthHandler:
    def __init__(self, angelos_api_key: str):
        self.angelos_api_key = angelos_api_key

    async def verify_api_key(self, x_api_key: str = Header(None)):
        if x_api_key != self.angelos_api_key:
            logging.error("Unauthorized access")
            raise HTTPException(status_code=403, detail="Unauthorized access")
