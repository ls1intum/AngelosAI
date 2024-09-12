import logging

from fastapi import HTTPException, APIRouter, status
from pydantic import BaseModel

from app.utils.dependencies import request_handler, weaviate_manager
from app.utils.environment import config
from app.utils.vector_store_initializer import initialize_vectorstores


class UserRequest(BaseModel):
    message: str
    study_program: str


router = APIRouter(prefix="/api/v1/question", tags=["response"])


@router.post("/ask")
async def ask(request: UserRequest):
    question = request.message
    classification = request.study_program
    if not question or not classification:
        raise HTTPException(status_code=400, detail="No question or classification provided")

    logging.info(f"Received question: {question} with classification: {classification}")
    answer = request_handler.handle_question(question, classification)
    logging.info(f"Generated answer: {answer}")
    return {"answer": answer}


@router.get("/initSchema",
            status_code=status.HTTP_202_ACCEPTED, )
async def ask():
    initialize_vectorstores(config.KNOWLEDGE_BASE_FOLDER, weaviate_manager)
    return


@router.post("/document")
async def add_document(request: UserRequest):
    question = request.message
    classification = request.study_program
    if not question or not classification:
        raise HTTPException(status_code=400, detail="No question or classification provided")

    logging.info(f"Received question: {question} with classification: {classification}")
    answer = request_handler.add_document(question, classification)
    logging.info(f"Generated answer: {answer}")
    return {"answer": answer}
