import logging
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException, APIRouter, status, Response, Header, Depends
from pydantic import BaseModel

from app.data.user_requests import UserChat
from app.injestion.vector_store_initializer import initialize_vectorstores
from app.utils.dependencies import request_handler, weaviate_manager, model
from app.utils.environment import config


class UserRequest(BaseModel):
    message: str
    study_program: str
    language: str


SECRET_KEY = config.API_ENDPOINT_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    """
    Generates a JWT token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != config.ANGELOS_APP_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access")


async def verify_token(authorization: str = Header(...)):
    """
    Dependency to validate the JWT token in the Authorization header.
    """
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


router = APIRouter(prefix="/api/v1/question", tags=["response"], dependencies=[Depends(verify_token)])
auth = APIRouter(prefix="/api", tags=["response"], dependencies=[Depends(verify_api_key)])


@auth.post("/token")
async def login():
    token_data = {"sub": "angular_app"}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/ask")
async def ask(request: UserRequest):
    question = request.message
    classification = request.study_program
    language = request.language
    if not question or not classification:
        raise HTTPException(status_code=400, detail="No question or classification provided")

    if len(question) > config.MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Question length exceeds the allowed limit of {config.MAX_MESSAGE_LENGTH} characters"
        )

    logging.info(f"Received question: {question} with classification: {classification}")

    if config.TEST_MODE:
        answer, used_tokens, general_context, specific_context = request_handler.handle_question_test_mode(question,
                                                                                                           classification,
                                                                                                           language)
        return {"answer": answer, "used_tokens": used_tokens, "general_context": general_context,
                "specific_context": specific_context}
    else:
        answer = request_handler.handle_question(question, classification, language)
        return {"answer": answer}


@router.post("/chat")
async def chat(request: UserChat):
    messages = request.messages
    if not messages:
        raise HTTPException(status_code=400, detail="No messages have been provided")

    last_message = messages[-1].message
    if len(last_message) > config.MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message length exceeds the allowed limit of {config.MAX_MESSAGE_LENGTH} characters"
        )

    logging.info(f"Received messages.")
    answer = request_handler.handle_chat(messages, study_program=request.study_program)
    return {"answer": answer}


@router.get("/initSchema",
            status_code=status.HTTP_202_ACCEPTED, )
async def initializeDb():
    initialize_vectorstores(config.KNOWLEDGE_BASE_FOLDER, config.QA_FOLDER, weaviate_manager)
    return


@router.post("/document")
async def add_document(request: UserRequest):
    question = request.message
    classification = request.study_program
    if not question or not classification:
        raise HTTPException(status_code=400, detail="No question or classification provided")

    logging.info(f"Received document: {question} with classification: {classification}")
    try:
        request_handler.add_document(question, classification)
        return Response(status_code=status.HTTP_200_OK)

    except Exception as e:
        logging.error(f"Failed to add document: {e}")
        raise HTTPException(status_code=500, detail="Failed to add document")


@router.get("/ping")
async def ping():
    logging.info(config.GPU_URL)
    return {"answer": "Server running."}


@router.get("/hi")
async def ping():
    logging.info("hi")
    return model.complete([{"role": "user", "content": "Hi"}])
