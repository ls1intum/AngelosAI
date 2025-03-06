from typing import Any

from openai.lib.azure import AzureOpenAI

from app.models.openai_model import OpenAIBaseModel


class AzureOpenAIBaseModel(OpenAIBaseModel):
    azure_endpoint: str
    azure_version: str

    def model_post_init(self, _context: Any, **kwargs):
        self._client = AzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_version=self.azure_version,
            api_key=self.api_key
        )
        self.init_model()
