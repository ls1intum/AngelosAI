import logging
from typing import Tuple, List, Any

from openai import OpenAI

from app.models.base_model import BaseModelClient


class OpenAIModel(BaseModelClient):
    api_key: str
    _client: OpenAI
    max_tokens: int = 800
    temperature: float = 0.5

    def model_post_init(self, __context: Any) -> None:
        self._client = OpenAI(api_key=self.api_key)

    def complete(self, messages: list) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        logging.info(f"Promt to OpenAI: {messages}")
        logging.info(f"Respones from OpenAI : {response}")
        return response.choices[0].message.content

    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content, response.usage.total_tokens

    def embed(self, text) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.emmodel
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.emmodel
        )
        return [e.embedding for e in response.data]

    def close_session(self):
        # Not required for this model
        return
