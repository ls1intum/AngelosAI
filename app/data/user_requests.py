from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    message: str
    type: str

class UserChat(BaseModel):
    messages: List[ChatMessage]
    study_program: Optional[str] = None
    orgId: int

class UserRequest(BaseModel):
    org_id: int
    message: str
    study_program: str
    language: str
