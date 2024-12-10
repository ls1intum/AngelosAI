from pydantic import BaseModel
from typing import List


class AddWebsiteRequest(BaseModel):
    id: int
    title: str
    link: str
    studyPrograms: List[str]
    content: str
    type: str

class RefreshContentRequest(BaseModel):
    content: str

class EditWebsiteRequest(BaseModel):
    title: str
    studyPrograms: List[int]

class AddDocumentRequest(BaseModel):
    id: int
    title: str
    studyPrograms: List[int]
    content: str

class EditDocumentRequest(BaseModel):
    title: str
    studyPrograms: List[int]

class AddSampleQuestionRequest(BaseModel):
    id: int
    question: str
    answer: str
    topic: str
    studyPrograms: List[int]

class EditSampleQuestionRequest(BaseModel):
    question: str
    answer: str
    topic: str
    studyPrograms: List[int]