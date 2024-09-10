import logging
import os
from typing import Dict
import requests
from app.models.base_model import BaseModelClient


def create_auth_header() -> Dict[str, str]:
    gpu_user = os.getenv("GPU_USER")
    gpu_password = os.getenv("GPU_PASSWORD")
    if gpu_user and gpu_password:
        return {
            'Authorization': requests.auth._basic_auth_str(gpu_user, gpu_password)
        }
    return {}


class OllamaModel(BaseModelClient):
    def __init__(self, model: str, url: str, embed_model: str):
        logging.info("Initializing OllamaModel")
        self.model = model
        self.url = url
        self.embed_model = embed_model
        self.headers = create_auth_header()

    def complete(self, messages: []) -> (str, float):
        response = requests.post(
            f"{self.url}chat",
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"logprobs": True, "temperature": 0.7}},
            headers=self.headers
        )
        response.raise_for_status()
        response_data = response.json()
        logging.info(f"Got response for model {self.model}: {response_data}")
        confidence = float(response_data['logprobs']['content']) if response_data.get('logprobs') and response_data[
            'logprobs'].get('content') is not None else 0.81
        return response_data["message"]["content"], confidence

    def embed(self, text):
        response = requests.post(
            f"{self.url}embeddings",
            json={"model": self.model, "prompt": text},
            headers=self.headers
        )
        logging.info(response)
        logging.info(response.headers)
        logging.info(response.elapsed.total_seconds())
        response.raise_for_status()
        response_data = response.json()
        # logging.info(f"Got response for model {self.model}: {response_data}")
        return response_data["embedding"]
