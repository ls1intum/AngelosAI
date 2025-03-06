from typing import List
import logging
from fastapi import HTTPException, APIRouter, status, Response, Depends
from app.data.knowledge_base_requests import AddWebsiteRequest, EditDocumentRequest, EditSampleQuestionRequest, EditWebsiteRequest, AddDocumentRequest, AddSampleQuestionRequest, RefreshContentRequest
from app.utils.dependencies import injestion_handler, auth_handler
from app.data.database_requests import DatabaseDocumentMetadata

knowledge_router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

# === Website Endpoints ===

@knowledge_router.post("/website/add", dependencies=[Depends(auth_handler.verify_api_key)])
async def add_website(body: AddWebsiteRequest):
    try:
        injestion_handler.add_website(body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)
    
@knowledge_router.post("/website/addBatch", dependencies=[Depends(auth_handler.verify_api_key)])
async def add_websites(body: List[AddWebsiteRequest]):
    try:
        injestion_handler.add_websites(body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/website/{id}/refresh", dependencies=[Depends(auth_handler.verify_api_key)])
async def refresh_website(id: str, body: RefreshContentRequest):
    try:
        injestion_handler.refresh_content(id=id, content=body.content)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/website/{id}/update", dependencies=[Depends(auth_handler.verify_api_key)])
async def update_website(id: str, body: EditWebsiteRequest):
    try:
        logging.info("Test")
        metadata: DatabaseDocumentMetadata = DatabaseDocumentMetadata(
            study_programs=body.studyPrograms,
            org_id=body.orgId
        )
        injestion_handler.update_database_document(id=id, metadata=metadata)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.delete("/website/{id}/delete", dependencies=[Depends(auth_handler.verify_api_key)])
async def delete_website(id: str):
    try:
        injestion_handler.delete_document(id=id)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)
    
@knowledge_router.delete("/website/deleteBatch", dependencies=[Depends(auth_handler.verify_api_key)])
async def delete_website(ids: List[str]):
    try:
        injestion_handler.delete_documents(ids=ids)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)


# === Document Endpoints ===

@knowledge_router.post("/document/add", dependencies=[Depends(auth_handler.verify_api_key)])
async def add_document(body: AddDocumentRequest):
    try:
        injestion_handler.add_document(body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/document/{id}/refresh", dependencies=[Depends(auth_handler.verify_api_key)])
async def refresh_document(id: str, body: RefreshContentRequest):
    try:
        injestion_handler.refresh_content(id=id, content=body.content)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/document/{id}/edit", dependencies=[Depends(auth_handler.verify_api_key)])
async def edit_document(id: str, body: EditDocumentRequest):
    try:
        metadata: DatabaseDocumentMetadata = DatabaseDocumentMetadata(
            study_programs=body.studyPrograms,
            org_id=body.orgId
        )
        injestion_handler.update_database_document(id=id, metadata=metadata)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.delete("/document/{id}/delete", dependencies=[Depends(auth_handler.verify_api_key)])
async def delete_document(id: str):
    try:
        injestion_handler.delete_document(id=id)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)
    
@knowledge_router.delete("/document/deleteBatch", dependencies=[Depends(auth_handler.verify_api_key)])
async def delete_document(body: List[str]):
    try:
        injestion_handler.delete_documents(ids=body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)


# === Sample Question Endpoints ===

@knowledge_router.post("/sample-question/add", dependencies=[Depends(auth_handler.verify_api_key)])
async def add_sample_question(body: AddSampleQuestionRequest):
    try:
        injestion_handler.add_sample_question(sample_question=body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)
    
@knowledge_router.post("/sample-question/addBatch", dependencies=[Depends(auth_handler.verify_api_key)])
async def add_sample_questions(body: List[AddSampleQuestionRequest]):
    try:
        injestion_handler.add_sample_questions(body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/sample-question/{id}/edit", dependencies=[Depends(auth_handler.verify_api_key)])
async def edit_sample_question(id: str, body: EditSampleQuestionRequest):
    try:
        injestion_handler.update_sample_question(kb_id=id, sample_question=body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.delete("/sample-question/{id}/delete", dependencies=[Depends(auth_handler.verify_api_key)])
async def delete_sample_question(id: str):
    try:
        injestion_handler.delete_sample_questions(ids=[id])
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)
    
@knowledge_router.delete("/sample-question/deleteBatch", dependencies=[Depends(auth_handler.verify_api_key)])
async def delete_sample_question(body: List[str]):
    try:
        injestion_handler.delete_sample_questions(ids=body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)