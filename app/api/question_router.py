import logging

from fastapi import HTTPException, APIRouter, Depends, Query

from app.data.user_requests import UserChat, UserRequest
from app.utils.dependencies import request_handler, auth_handler
from app.utils.environment import config

question_router = APIRouter(prefix="/api/v1/question", tags=["response"])


@question_router.post("/ask", tags=["email"], dependencies=[Depends(auth_handler.verify_api_key)])
async def ask(request: UserRequest):
    question = request.message
    classification = request.study_program.lower()
    language = request.language.lower()
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
        if language == "german":
            answer += "\n\n**Diese Antwort wurde automatisch generiert.**"
        else:
            answer += "\n\n**This answer was automatically generated.**"
        
        return {"answer": answer, "used_tokens": used_tokens, "general_context": general_context,
                "specific_context": specific_context}
    else:
        answer = request_handler.handle_question(question, classification, language)
        if language == "german":
            answer += "\n\n**Diese Antwort wurde automatisch generiert.**"
        else:
            answer += "\n\n**This answer was automatically generated.**"
        
        return {"answer": answer}


@question_router.post("/chat", tags=["chatbot"], dependencies=[Depends(auth_handler.verify_api_key)])
async def chat(
    request: UserChat,
    filterByOrg: bool = Query(..., description="Indicates whether to filter context by organization")
):
    messages = request.messages
    org_id = request.orgId

    if not messages:
        raise HTTPException(status_code=400, detail="No messages have been provided")
        
    answer = request_handler.handle_chat(
        messages,
        study_program=request.study_program,
        org_id=org_id,
        filter_by_org=filterByOrg
    )

    return {"answer": answer}
