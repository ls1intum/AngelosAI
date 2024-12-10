from fastapi import HTTPException, APIRouter, status, Response, Depends
from app.data.knowledge_base_requests import AddWebsiteRequest, EditDocumentRequest, EditSampleQuestionRequest, EditWebsiteRequest, AddDocumentRequest, AddSampleQuestionRequest, RefreshContentRequest
from app.utils.dependencies import injestion_handler
from app.data.database_requests import DatabaseDocumentMetadata

knowledge_router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@knowledge_router.post("/website/add")
async def add_website(body: AddWebsiteRequest):
    try:
        injestion_handler.add_website(body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/website/{id}/refresh")
async def refresh_website(id: int, body: RefreshContentRequest):
    try:
        injestion_handler.refresh_content(id=id, content=body.content)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/website/{id}/update")
async def update_website(id: int, body: EditWebsiteRequest):
    try:
        metadata: DatabaseDocumentMetadata = DatabaseDocumentMetadata(
            study_programs=body.studyPrograms
        )
        injestion_handler.update_database_document(id=id, metadata=metadata)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.delete("/website/{id}/delete")
async def delete_website(id: int):
    try:
        injestion_handler.delete_document(id=id)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)


# === Document Endpoints ===

@knowledge_router.post("/document/add")
async def add_document(body: AddDocumentRequest):
    try:
        injestion_handler.add_document(body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/document/{id}/refresh")
async def refresh_document(id: int, body: RefreshContentRequest):
    try:
        injestion_handler.refresh_content(id=id, content=body.content)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/document/{id}/edit")
async def edit_document(id: int, body: EditDocumentRequest):
    try:
        metadata: DatabaseDocumentMetadata = DatabaseDocumentMetadata(
            study_programs=body.studyPrograms
        )
        injestion_handler.update_database_document(id=id, metadata=metadata)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.delete("/document/{id}/delete")
async def delete_document(id: int):
    try:
        injestion_handler.delete_document(id=id)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)


# === Sample Question Endpoints ===

@knowledge_router.post("/sample-question/add")
async def add_sample_question(body: AddSampleQuestionRequest):
    try:
        injestion_handler.add_sample_question(sample_question=body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.post("/sample-question/{id}/edit")
async def edit_sample_question(id: int, body: EditSampleQuestionRequest):
    try:
        injestion_handler.update_sample_question(kb_id=id, sample_question=body)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)

@knowledge_router.delete("/sample-question/{id}/delete")
async def delete_sample_question(id: int):
    try:
        injestion_handler.delete_sample_question(id=id)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500)