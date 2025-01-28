import logging

from openai.lib.azure import AzureOpenAI

from app.models.openai_base_model import OpenAIBaseModel


class AzureOpenAIModel(OpenAIBaseModel):
    api_key: str
    api_version: str
    azure_endpoint: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = AzureOpenAI(api_key=self.api_key, api_version=self.api_version,
                                   azure_endpoint=self.azure_endpoint)
        logging.info("Azure OpenAI client initialized.")
