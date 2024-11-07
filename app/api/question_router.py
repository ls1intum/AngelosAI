import logging

from fastapi import HTTPException, APIRouter, status, Response, Depends

from app.data.user_requests import UserChat, UserRequest
from app.injestion.vector_store_initializer import initialize_vectorstores
from app.managers.auth_handler import LoginRequest
from app.utils.dependencies import request_handler, auth_handler, weaviate_manager, model
from app.utils.environment import config

question_router = APIRouter(prefix="/api/v1/question", tags=["response"])
admin_router = APIRouter(prefix="/api/admin", tags=["settings", "admin"],
                         dependencies=[Depends(auth_handler.verify_token)])
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


@question_router.post("/ask", tags=["email"], dependencies=[Depends(auth_handler.verify_api_key)])
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


@question_router.post("/chat", tags=["chatbot"], dependencies=[Depends(auth_handler.verify_token)])
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


@admin_router.get("/initSchema",
                  status_code=status.HTTP_202_ACCEPTED, )
async def initializeDb():
    initialize_vectorstores(config.KNOWLEDGE_BASE_FOLDER, config.QA_FOLDER, weaviate_manager)
    return


@admin_router.post("/document")
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


@admin_router.get("/ping")
async def ping():
    logging.info(config.GPU_URL)
    return {"answer": "Server running."}


@admin_router.get("/hi")
async def ping():
    logging.info("hi")
    return model.complete([{"role": "user", "content": "Hi"}])
