import logging
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException, Header
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthHandler:
    def __init__(self, angelos_api_key: str, secret_key: str, algorithm: str, access_token_expires_minutes: float):
        self.angelos_api_key = angelos_api_key
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expires_minutes = access_token_expires_minutes

    def create_access_token(self, data: dict):
        """
        Generates a JWT token with an expiration time.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expires_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def verify_api_key(self, x_api_key: str = Header(None)):
        if x_api_key != self.angelos_api_key:
            logging.error("Unauthorized access")
            raise HTTPException(status_code=403, detail="Unauthorized access")

    async def verify_token(self, authorization: str = Header(...)):
        """
        Dependency to validate the JWT token in the Authorization header.
        """
        try:
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            logging.error("Token has expired")
            raise HTTPException(status_code=403, detail="Token has expired")
        except jwt.PyJWTError:
            logging.error("Invalid token")
            raise HTTPException(status_code=403, detail="Invalid token")
