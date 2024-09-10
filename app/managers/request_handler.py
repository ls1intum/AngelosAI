import logging

from pydantic import BaseModel


class RequestHandler:
    def __init__(self, weaviate_manager, prompt_manager):
        self.weaviate_manager = weaviate_manager
        self.prompt_manager = prompt_manager

    def handle_question(self, question: str, classification: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        general_context = self.weaviate_manager.get_relevant_context(question, "general")
        specific_context = self.weaviate_manager.get_relevant_context(question, classification)
        prompt = self.prompt_manager.format_prompt(general_context, specific_context, question)
        return self.weaviate_manager.model.complete(prompt)

