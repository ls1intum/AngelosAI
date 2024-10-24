from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    message: str
    type: str

class UserChat(BaseModel):
    messages: List[ChatMessage]
    study_program: str

class SampleQuestion(BaseModel):
    topic: str
    question: str
    answer: str
    study_program: str

class WebsiteContent(BaseModel):
    type: str
    content: str
    link: str
    study_program: str
