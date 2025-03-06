import logging
from typing import Any

from openai import OpenAI

from app.models.base_model import BaseModelClient


class OpenAIBaseModel(BaseModelClient):
    api_key: str
    temperature: float = 0.3
    _client: OpenAI

    def model_post_init(self, __context: Any) -> None:
        self._client = OpenAI(api_key=self.api_key)
        self.init_model()

    def complete(self, prompt: list) -> str:
        response = self._client.chat.completions.create(
            messages=prompt,
            model=self.model,
            temperature=self.temperature
        )
        logging.info(f"Got response for model {self.model}: {response}")
        return response.choices[0].message.content
    
    def init_model(self) -> None:
        logging.info("Initializing model...")
