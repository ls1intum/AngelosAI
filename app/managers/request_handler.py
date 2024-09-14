from app.managers.weaviate_manager import WeaviateManager
from app.models.base_model import BaseModelClient
from app.prompt.prompt_manager import PromptManager

class RequestHandler:
    def __init__(self, weaviate_manager: WeaviateManager, model: BaseModelClient, prompt_manager: PromptManager):
        self.weaviate_manager = weaviate_manager
        self.model = model
        self.prompt_manager = prompt_manager

    def handle_question(self, question: str, classification: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        general_context = self.weaviate_manager.get_relevant_context(question, "general")
        if classification != "general":
            specific_context = self.weaviate_manager.get_relevant_context(question, classification)
        messages = self.prompt_manager.create_messages(general_context, specific_context, question)

        return self.model.complete(messages)
    
    def handle_question_test_mode(self, question: str, classification: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        general_context, general_context_list = self.weaviate_manager.get_relevant_context_as_list(question, "general")
        if classification != "general":
            specific_context, specific_context_list = self.weaviate_manager.get_relevant_context_as_list(question, classification)
        else:
            specific_context_list = []
        messages = self.prompt_manager.create_messages(general_context, specific_context, question)
        answer, tokens = self.model.complete_with_tokens(messages)
        return answer, tokens, general_context_list, specific_context_list

    def add_document(self, question: str, classification: str):
        return self.weaviate_manager.add_document(question, classification)
