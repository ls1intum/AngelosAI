import logging

from openai import OpenAI

from app.models.openai_model import OpenAIBaseModel


class LocalBaseModel(OpenAIBaseModel):
    api_key: str
    endpoint: str
    model: str
    max_tokens: int = 800
    temperature: float = 0.3

    def __init__(self, endpoint, api_key: str, **kwargs):
        client = OpenAI(base_url=endpoint, api_key=api_key)
        logging.info("Local lms API key set.")
