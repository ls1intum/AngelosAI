import logging
from typing import Any

from openai import OpenAI

from app.models.base_model import BaseModelClient


class OpenAIBaseModel(BaseModelClient):
    api_key: str
    temperature: float = 0.3
    _client: OpenAI

    def model_post_init(self, __context: Any) -> None:
        self._client = OpenAI(api_key=self.api_key)
        self.init_model()

    def complete(self, prompt: list) -> str:
        json_schema = {
            "name": "email_classification",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "classification": {
                        "type": "string",
                        "enum": ["non-sensitive", "sensitive"]
                    },
                    "language": {
                        "type": "string",
                        "enum": ["german", "english"]
                    },
                    "study_program": {
                        "type": "string"
                    },
                    "is_colleague": {
                        "type": "boolean"
                    }
                },
                "required": ["classification", "language", "study_program", "is_colleague"],
                "additionalProperties": False
            }
        }
        
        response = self._client.chat.completions.create(
            messages=prompt,
            model=self.model,
            temperature=self.temperature,
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            }
        )
        logging.info(f"Got response for model {self.model}: {response}")
        return response.choices[0].message.content
    
    def init_model(self) -> None:
        logging.info("Initializing model...")
