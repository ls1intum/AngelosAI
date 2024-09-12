import logging
from typing import Dict

import requests

from app.models.base_model import BaseModelClient
from app.utils.environment import config


def create_auth_header() -> Dict[str, str]:
    gpu_user = config.GPU_USER
    gpu_password = config.GPU_PASSWORD
    host = config.GPU_HOST
    if gpu_user and gpu_password:
        return {
            'Authorization': requests.auth._basic_auth_str(gpu_user, gpu_password),
        }
    return {}


class OllamaModel(BaseModelClient):
    def __init__(self, model: str, url: str, embed_model: str, session=None):
        self.session = session or requests.Session()
        logging.info("Initializing OllamaModel")
        self.model = model
        self.url = url
        self.embed_model = embed_model
        self.headers = create_auth_header()
        self.init_model()

    def complete(self, messages: []) -> (str, float):
        logging.info(messages)
        logging.info("WTF")

        response = self.session.post(
            f"{self.url}chat",
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"logprobs": True, "temperature": 0.7}},
            headers=self.headers
        )
        response_data = response.json()
        logging.info(f"Got response for model {self.model}: {response_data}")
        response.raise_for_status()
        confidence = float(response_data['logprobs']['content']) if response_data.get('logprobs') and response_data[
            'logprobs'].get('content') is not None else 0.81
        return response_data["message"]["content"], confidence

    def completeSingle(self, prompt: str) -> (str, float):
        response = self.session.post(
            f"{self.url}chat",
            json={"model": self.model, "prompt": prompt, "stream": False,
                  "options": {"logprobs": True, "temperature": 0.7}},
            headers=self.headers
        )
        response_data = response.json()
        logging.info(f"Got response for model {self.model}: {response_data}")
        response.raise_for_status()
        confidence = float(response_data['logprobs']['content']) if response_data.get('logprobs') and response_data[
            'logprobs'].get('content') is not None else 0.81

        logging.info(f"Confidence = {confidence}")
        return response_data["message"]["content"], confidence

    def embed(self, text):
        response = self.session.post(
            f"{self.url}embeddings",
            json={"model": self.embed_model, "prompt": text},
            headers=self.headers
        )
        # logging.info(response)
        # logging.info(response.headers)
        logging.info(response.elapsed.total_seconds())
        response.raise_for_status()
        response_data = response.json()
        # logging.info(f"Got response for model {self.model}: {response_data}")
        return response_data["embedding"]

    def close_session(self):
        # Close the session when done
        if self.session:
            self.session.close()

    def init_model(self):
        self.session.post(
            f"{self.url}tags",
            json={"model": self.model},
            headers=self.headers
        )
