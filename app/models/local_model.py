import logging

from openai import OpenAI

from app.models.openai_base_model import OpenAIBaseModel


class LocalModel(OpenAIBaseModel):
    api_key: str
    endpoint: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = OpenAI(base_url=self.endpoint, api_key=self.api_key)
        logging.info("Local lms API key set.")
