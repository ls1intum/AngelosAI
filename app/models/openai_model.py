import logging

from openai import OpenAI

from app.models.base_model import BaseModelClient


class OpenAIModel(BaseModelClient):
    def __init__(self, api_key: str, url: str):
        logging.info("Initializing OpenAIModel")
        self._client = OpenAI(base_url=url, api_key=api_key)

    def complete(self, messages: []) -> (str, float):
        response = self._client.chat.completions.create(
            messages=messages,
            logprobs=True
        )
        logging.info(f"Got prompt: {messages}")
        logging.info(f"Got : {response}")
        confidence = float(response['logprobs']['content']) if response.get('logprobs') and response['logprobs'].get(
            'content') is not None else 0.81
        return response.choices[0]["message"]["content"], confidence

    def completeSingle(self, prompt: str) -> (str, float):
        response = self._client.chat.completions.create(
            prompt=prompt,
            logprobs=True
        )
        logging.info(f"Got prompt: {prompt}")
        logging.info(f"Got : {response}")
        confidence = float(response['logprobs']['content']) if response.get('logprobs') and response['logprobs'].get(
            'content') is not None else 0.81
        return response.choices[0]["message"]["content"], confidence

    def embed(self, text, model="text-embedding-3-small"):
        return self._client.embeddings.create(input=[text], model=model).data[0].embedding
