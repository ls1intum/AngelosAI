from pydantic import BaseModel
from typing import List, Optional

class DatabaseDocument(BaseModel):
    id: str
    link: Optional[str] = None
    study_programs: List[str]
    content: str
    org_id: int
    
class DatabaseDocumentMetadata(BaseModel):
    link: Optional[str] = None
    study_programs: List[str]
    org_id: int
    
class DatabaseSampleQuestion(BaseModel):
    id: str
    topic: str
    question: str
    answer: str
    study_programs: List[str]
    org_id: int
