import logging
from typing import Dict, Tuple, List, Optional, Any

import requests
from pydantic import ConfigDict

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
    url: str
    headers: Optional[Dict[str, str]] = None
    session: requests.Session = requests.Session()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        logging.info("Initializing OllamaModel")
        self.headers = create_auth_header()
        self.init_model()

    def complete(self, messages: list) -> str:
        response = self.session.post(
            f"{self.url}chat",
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"logprobs": True, "temperature": 0.7}},
            headers=self.headers
        )
        response_data = response.json()
        logging.info(f"Got response for model {self.model}: {response_data}")
        response.raise_for_status()
        # confidence = float(response_data['logprobs']['content']) if response_data.get('logprobs') and response_data[
        #     'logprobs'].get('content') is not None else 0.81
        # return response_data["message"]["content"], confidence
        return response_data["message"]["content"]

    # TODO: Implement getting the tokens
    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        response = self.session.post(
            f"{self.url}chat",
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"logprobs": True, "temperature": 0.7}},
            headers=self.headers
        )
        response_data = response.json()
        logging.info(f"Got response for model {self.model}: {response_data}")
        response.raise_for_status()
        return response_data["message"]["content"], -1

    def embed(self, text) -> List[float]:
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

        return response_data["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("TODO: IMPLEMENT THIS METHOD IF POSSIBLE")

    def close_session(self):
        # Close the session when done
        if self.session:
            self.session.close()

    def init_model(self):
        logging.info("Initializing Ollama model")
        self.complete([{"role": "user", "content": "Hi"}])
