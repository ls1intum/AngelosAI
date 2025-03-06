import logging
from typing import Dict, Any, Optional

import requests
from pydantic import ConfigDict
from requests import Timeout, HTTPError, RequestException

from app.common.environment import config
from app.models.base_model import BaseModelClient


def create_auth_header() -> Dict[str, str]:
    gpu_user = config.GPU_USER
    gpu_password = config.GPU_PASSWORD
    if gpu_user and gpu_password:
        return {
            'Authorization': requests.auth._basic_auth_str(gpu_user, gpu_password)
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

    def complete(self, prompt: list) -> str:
        logging.info("Requesting model response")

        try:
            # Making the request with a timeout
            response = self.session.post(
                f"{self.url}chat",
                json={"model": self.model, "messages": prompt, "stream": False,
                      "options": {"temperature": 0.2, "max_tokens": 128}, "format": "json"},

                headers=self.headers,
            )
            response.raise_for_status()

        except Timeout:
            logging.error("Request timed out")
            return None

        except HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return None

        except RequestException as req_err:
            logging.error(f"Error during request: {req_err}")
            return None
        try:
            response_data = response.json()
            logging.info(f"Got response for model {self.model}: {response_data}")
        except ValueError as json_err:
            logging.error(f"JSON decoding failed: {json_err}")
            return None

        message_content = response_data.get("message", {}).get("content")

        if message_content is None:
            logging.warning("Message content is missing in the response")
            return None

        # logging.info(f"Received prompt: {prompt}")
        return message_content

    def close_session(self):
        if self.session:
            self.session.close()

    def init_model(self):
        if not self.initialized_model:
            logging.info("Initializing Ollama model")
            self.complete([{"role": "user", "content": "Hi"}])
            self.initialized_model = True
            logging.info("Initialized Ollama model")
