import logging

from app.email_service.email_dto import EmailDTO
from app.models.ollama_model import BaseModelClient


class Classifier:
    def __init__(self, model: BaseModelClient):
        self.model = model

    def classify(self, email: EmailDTO):
        logging.info("This should be implemented")
        return

    def request_llm(self, prompt):
        logging.info(f"Requesting LLM")
        return self.model.complete(prompt)

