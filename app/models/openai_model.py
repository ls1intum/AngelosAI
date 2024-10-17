import logging
from typing import Tuple, List, Any
from pydantic import model_validator

import openai

from app.models.base_model import BaseModelClient


class OpenAIModel(BaseModelClient):
    api_key: str
    model: str
    embed_model: str
    max_tokens: int = 800
    temperature: float = 0.3

    @model_validator(mode="before")
    def initialize_openai(cls, values):
        openai.api_key = values.get("api_key")
        openai.api_type = "openai"
        logging.info("OpenAI API key set.")
        return values

    # def model_post_init(self, __context: Any) -> None:
        # self._client = OpenAI(api_key=self.api_key)

    def complete(self, messages: list) -> str:
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content, response.usage.total_tokens

    def embed(self, text) -> List[float]:
        response = openai.embeddings.create(
            input=text,
            model=self.embed_model
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = openai.embeddings.create(
            input=texts,
            model=self.embed_model
        )
        return [e.embedding for e in response.data]

    def close_session(self):
        # Not required for this model
        return
