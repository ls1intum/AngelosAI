import logging
from typing import Any, List, Tuple

from app.models.base_model import BaseModelClient


class OpenAIBaseModel(BaseModelClient):
    _client: Any

    def complete(self, messages: list) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
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

    def embed(self, text: str) -> List[float]:
        try:
            response = self._client.embeddings.create(
                model=self.embed_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error("Error occurred while creating embeddings: %s", str(e))
            # Optionally, re-raise the exception or handle it as needed
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self._client.embeddings.create(
            model=self.embed_model,
            input=texts
        )
        return [item.embedding for item in response.data]
