from typing import List, Tuple

class BaseModelClient:
    def complete(self, messages: list) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("This method should be implemented by subclasses.")
