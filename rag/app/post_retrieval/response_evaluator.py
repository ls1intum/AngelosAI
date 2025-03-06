import logging

from app.models.base_model import BaseModelClient
from app.prompt.prompt_manager import PromptManager


class ResponseEvaluator:
    def __init__(self, model: BaseModelClient, prompt_manager: PromptManager):
        self.model = model
        self.prompt_manager = prompt_manager

    def process_response(self, question: str, response: str, language: str) -> str:
        if response != "False":
            response_valid: bool = self.evaluate_response(question=question, response=response, language=language)
            if response_valid:
                if language == "german":
                    response += "\n\n**Diese Antwort wurde automatisch generiert.**"
                else:
                    response += "\n\n**This answer was automatically generated.**"
            else:
                response = "False"
        return response

    def evaluate_response(self, question: str, response: str, language: str) -> bool:
        prompt = self.prompt_manager.create_response_evaluation_messages(question=question, answer=response,
                                                                         language=language)
        output = self.model.complete(prompt).strip()

        if "OK" in output:
            return True
        else:
            logging.error("LLM as a judge does not think the answer is appropriate.")
            return False
