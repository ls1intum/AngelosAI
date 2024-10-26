from typing import Any, List, Tuple
import logging

from pydantic import model_validator
from openai.lib.azure import AzureOpenAI

from app.models.base_model import BaseModelClient


class AzureOpenAIModel(BaseModelClient):
    api_key: str
    api_version: str
    azure_endpoint: str
    model: str  # Deployment name for chat completions
    embed_model: str  # Deployment name for embeddings
    max_tokens: int = 800
    temperature: float = 0.3
    _client: AzureOpenAI

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint
        )
        logging.info("Azure OpenAI client initialized.")

    def complete(self, messages: list) -> str:
        response = self._client.chat.completions.create(
            model=self.model,  # Deployment name for chat model
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        content = response.choices[0].message.content
        total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else None
        return content, total_tokens

    def embed(self, text) -> List[float]:
        response = self._client.embeddings.create(
            model=self.embed_model,  # Deployment name for embeddings
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self._client.embeddings.create(
            model=self.embed_model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def close_session(self):
        # No explicit session to close in this client
        pass