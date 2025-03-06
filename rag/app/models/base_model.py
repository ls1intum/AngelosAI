import logging
from typing import List, Tuple

from pydantic import BaseModel


class BaseModelClient(BaseModel):
    model: str
    embed_model: str
    max_tokens: int = 800
    temperature: float = 0.3

    def complete(self, messages: list) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def embed(self, text: str) -> List[float]:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def close_session(self):
        logging.info("Model has been shutdown.")
