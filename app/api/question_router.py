import logging

from fastapi import HTTPException, APIRouter, status, Response
from pydantic import BaseModel

from app.data.user_requests import UserChat
from app.injestion.vector_store_initializer import initialize_vectorstores
from app.utils.dependencies import request_handler, weaviate_manager, model
from app.utils.environment import config


class UserRequest(BaseModel):
    message: str
    study_program: str
    language: str


router = APIRouter(prefix="/api/v1/question", tags=["response"])


@router.post("/ask")
async def ask(request: UserRequest):
    question = request.message
    classification = request.study_program
    language = request.language
    if not question or not classification:
        raise HTTPException(status_code=400, detail="No question or classification provided")

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
    logging.info(config.OLLAMA_URL)
    return {"answer": "Server running."}


@router.get("/hi")
async def ping():
    logging.info("hi")
    return model.complete([{"role": "user", "content": "Hi"}])
