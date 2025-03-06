import logging
from typing import Dict, Tuple, List, Optional, Any

import requests
from pydantic import ConfigDict

from app.models.base_model import BaseModelClient
from app.utils.environment import config


def create_auth_header() -> Dict[str, str]:
    gpu_user = config.GPU_USER
    gpu_password = config.GPU_PASSWORD
    if gpu_user and gpu_password:
        return {
            'Authorization': requests.auth._basic_auth_str(gpu_user, gpu_password),
        }
    return {}


class OllamaModel(BaseModelClient):
    url: str
    headers: Optional[Dict[str, str]] = None
    session: requests.Session = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
    initialized_model: bool = False

    def model_post_init(self, __context: Any) -> None:
        logging.info("Initializing OllamaModel")
        self.session = requests.Session()
        self.headers = create_auth_header()
        self.init_model()

    def complete(self, messages: list) -> str:
        try:
            logging.info("OllamaModel")
            response = self.session.post(
                f"{self.url}chat",
                json={"model": self.model, "messages": messages, "stream": False,
                      "options": {"logprobs": True, "temperature": self.temperature, "num_predict": self.max_tokens}},
                headers=self.headers
            )
            logging.info(f"Server response time chat: {response.elapsed.total_seconds():.4f} seconds")
            response_data = response.json()
            response.raise_for_status()
            return response_data["message"]["content"]
        except Exception as e:
            logging.error(e)
        # confidence = float(response_data['logprobs']['content']) if response_data.get('logprobs') and response_data[
        #     'logprobs'].get('content') is not None else 0.81
        # return response_data["message"]["content"], confidence

    # TODO: Implement getting the tokens
    def complete_with_tokens(self, messages: list) -> Tuple[str, int]:
        response = self.session.post(
            f"{self.url}chat",
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"logprobs": True, "temperature": 0.7}},
            headers=self.headers
        )
        response_data = response.json()
        response.raise_for_status()
        return response_data["message"]["content"], -1

    def embed(self, text) -> List[float]:
        try:
            response = self.session.post(
                f"{self.url}embeddings",
                json={"model": self.embed_model, "prompt": text},
                headers=self.headers
            )
            logging.info(f"Server response time embed: {response.elapsed.total_seconds():.4f} seconds")
            response.raise_for_status()
            response_data = response.json()
            return response_data["embedding"]
        except Exception as e:
            logging.error(e)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("TODO: IMPLEMENT THIS METHOD IF POSSIBLE")

    def close_session(self):
        """Close session when done"""
        if self.session:
            self.session.close()

    def init_model(self):
        """Make sure the model is initialized once, not on every request."""
        if not self.initialized_model:
            logging.info("Initializing Ollama model")
            self.complete([{"role": "user", "content": "Hi"}])
            self.initialized_model = True
            logging.info("Initialized Ollama model")
