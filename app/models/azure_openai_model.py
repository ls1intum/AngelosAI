from typing import Any

from openai.lib.azure import AzureOpenAI

from app.models.openai_model import OpenAIModel


class AzureOpenAIModel(OpenAIModel):
    azure_deployment: str
    _client: AzureOpenAI

    def model_post_init(self, __context: Any) -> None:
        self._client = AzureOpenAI(
            azure_deployment=self.azure_deployment,
        )
