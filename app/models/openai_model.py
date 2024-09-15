import logging
from typing import Tuple, List
import openai

from app.models.base_model import BaseModelClient


class OpenAIModel(BaseModelClient):
    def __init__(self, api_key: str, url: str):
        self.model = "gpt-4o-mini"
        self.max_tokens = 800
        self.temperature = 0.5
        openai.api_key = api_key
        self.emmodel = "text-embedding-3-small"
        

    def complete(self, messages: list) -> str:
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        logging.info(f"Promt to OpenAI: {messages}")
        logging.info(f"Respones from OpenAI : {response}")
        return response.choices[0].message.content
    
    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return (response.choices[0].message.content, response.usage.total_tokens)

    
    def embed(self, text) -> List[float]:
        response = openai.embeddings.create(
            input=text,
            model=self.emmodel
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = openai.embeddings.create(
            input=texts,
            model=self.emmodel
        )
        return [e.embedding for e in response.data]
    
    def close_session(self):
        # Not required for this model
        return
