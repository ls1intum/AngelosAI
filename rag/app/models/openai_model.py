import logging

import openai

from app.models.openai_base_model import OpenAIBaseModel


class OpenAIModel(OpenAIBaseModel):
    api_key: str
    model: str
    embed_model: str
    max_tokens: int = 800
    temperature: float = 0.3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        openai.api_key = self.api_key
        openai.api_type = "openai"
        self._client = openai
        logging.info("OpenAI API key set.")
