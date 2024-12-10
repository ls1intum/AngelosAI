import logging

from fastapi import HTTPException, APIRouter, status, Response, Depends

from app.utils.dependencies import request_handler, auth_handler, weaviate_manager, model
from app.injestion.vector_store_initializer import initialize_vectorstores
from app.utils.environment import config
from app.data.user_requests import UserChat, UserRequest


admin_router = APIRouter(prefix="/api/admin", tags=["settings", "admin"],
                         dependencies=[Depends(auth_handler.verify_token)])

# TODO: Remove
@admin_router.get("/initSchema",
                  status_code=status.HTTP_202_ACCEPTED, )
async def initializeDb():
    initialize_vectorstores(config.KNOWLEDGE_BASE_FOLDER, config.QA_FOLDER, weaviate_manager)
    return


# TODO: Remove
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