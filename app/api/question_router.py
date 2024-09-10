import logging

from fastapi import HTTPException, FastAPI, APIRouter, Depends
from pydantic import BaseModel

from app.managers.request_handler import RequestHandler
from app.managers.weaviate_manager import WeaviateManager
from app.prompt.prompt_manager import PromptManager


class Request(BaseModel):
    message: str
    study_program: str


router = APIRouter(prefix="/api/v1/question", tags=["response"])


def get_request_handler(weaviate_manager: WeaviateManager = Depends()):
    prompt_manager = PromptManager()
    return RequestHandler(weaviate_manager, prompt_manager)


@router.post("/ask")
async def ask(request: Request, request_handler: RequestHandler = Depends(get_request_handler)):
    question = request.message
    classification = request.classification
    if not question or not classification:
        raise HTTPException(status_code=400, detail="No question or classification provided")

    logging.info(f"Received question: {question} with classification: {classification}")
    answer = request_handler.handle_question(question, classification)
    logging.info(f"Generated answer: {answer}")
    return {"answer": answer}
