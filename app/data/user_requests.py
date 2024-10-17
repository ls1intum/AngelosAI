from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str
    type: str

    def __str__(self):
        return f"{self.type}:  {self.message}"


class UserChat(BaseModel):
    messages: list[ChatMessage]
    study_program: str
