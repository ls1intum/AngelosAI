from pydantic import BaseModel


class BaseModelClient(BaseModel):
    model: str
    
    def complete(self, prompt: []) -> (str, float):
        raise NotImplementedError("This method should be implemented by subclasses.")
