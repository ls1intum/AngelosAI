from pydantic import BaseModel
from typing import List


class AddWebsiteRequest(BaseModel):
    id: str
    orgId: int
    title: str
    link: str
    studyPrograms: List[str]
    content: str
    type: str

class RefreshContentRequest(BaseModel):
    content: str

class EditWebsiteRequest(BaseModel):
    title: str
    studyPrograms: List[str]

class AddDocumentRequest(BaseModel):
    id: str
    orgId: int
    title: str
    studyPrograms: List[str]
    content: str

class EditDocumentRequest(BaseModel):
    title: str
    studyPrograms: List[str]

class AddSampleQuestionRequest(BaseModel):
    id: str
    orgId: int
    question: str
    answer: str
    topic: str
    studyPrograms: List[str]

class EditSampleQuestionRequest(BaseModel):
    question: str
    answer: str
    topic: str
    studyPrograms: List[str]
    orgId: int