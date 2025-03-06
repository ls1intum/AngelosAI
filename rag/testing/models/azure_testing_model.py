from typing import List
from openai import AzureOpenAI

class AzureTestingModel:
    def __init__(self, api_key: str, api_version: str, azure_endpoint: str, 
                 model: str, embed_model: str, max_tokens: int = 200, temperature: float = 0):
        self.api_key = api_key
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint
        self.model = model
        self.embed_model = embed_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize the AzureOpenAI client
        self._client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint
        )

    def complete(self, messages: list) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def embed(self, text) -> List[float]:
        response = self._client.embeddings.create(
            model=self.embed_model,
            input=text
        )
        return response.data[0].embedding