from pydantic import BaseModel
from typing import List, Optional

class DatabaseDocument(BaseModel):
    id: int
    link: Optional[str] = None
    study_programs: List[str]
    content: str
    
class DatabaseDocumentMetadata(BaseModel):
    link: Optional[str] = None
    study_programs: List[str]
    
class DatabaseSampleQuestion(BaseModel):
    id: int
    topic: str
    question: str
    answer: str
    study_programs: List[str]
