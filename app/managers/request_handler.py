from typing import List

from app.data.user_requests import ChatMessage
from app.managers.weaviate_manager import WeaviateManager
from app.models.base_model import BaseModelClient
from app.prompt.prompt_manager import PromptManager
from app.utils.language_detector import LanguageDetector


class RequestHandler:
    def __init__(self, weaviate_manager: WeaviateManager, model: BaseModelClient, prompt_manager: PromptManager):
        self.weaviate_manager = weaviate_manager
        self.model = model
        self.prompt_manager = prompt_manager

    def handle_question(self, question: str, classification: str, language: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        # Get relevant keywords
        # messages = self.prompt_manager.create_keyword_extraction_message(question)
        # answer, tokens = self.model.complete_with_tokens(messages)
        # logging.info(f"LLM Keyword extraction: {answer}, with tokens used: {tokens}")
        # keywords = answer.replace(",", "")

        general_context = self.weaviate_manager.get_relevant_context(question=question, study_program="general",
                                                                     language=language)
        specific_context = None
        if classification != "general":
            specific_context = self.weaviate_manager.get_relevant_context(question=question,
                                                                          study_program=classification,
                                                                          language=language)
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=question, language=language)
        sample_questions_formatted = self.prompt_manager.format_sample_questions(sample_questions, language)
        messages = self.prompt_manager.create_messages(general_context, specific_context, sample_questions_formatted,
                                                       question, language)

        return self.model.complete(messages)

    def handle_question_test_mode(self, question: str, classification: str, language: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        # Get relevant keywords
        # messages = self.prompt_manager.create_keyword_extraction_message(question)
        # answer, tokens = self.model.complete_with_tokens(messages)
        # logging.info(f"LLM Keyword extraction: {answer}, with tokens used: {tokens}")
        # keywords = answer.replace(",", "")

        general_context, general_context_list = self.weaviate_manager.get_relevant_context(question=question,
                                                                                           study_program="general",
                                                                                           language=language,
                                                                                           test_mode=True)
        specific_context = None
        if classification != "general":
            specific_context, specific_context_list = self.weaviate_manager.get_relevant_context(question=question,
                                                                                                 study_program=classification,
                                                                                                 language=language,
                                                                                                 test_mode=True)
        else:
            specific_context_list = []
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=question, language=language)
        sample_questions_formatted = self.prompt_manager.format_sample_questions(sample_questions, language)
        messages = self.prompt_manager.create_messages(general_context, specific_context, sample_questions_formatted,
                                                       question, language)
        answer, tokens = self.model.complete_with_tokens(messages)
        return answer, tokens, general_context_list, specific_context_list

    def add_document(self, question: str, classification: str):
        return self.weaviate_manager.add_document(question, classification)

    def handle_chat(self, messages: List[ChatMessage], study_program: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        last_message = messages[-1].message
        lang = LanguageDetector.get_language(last_message)

        general_context = self.weaviate_manager.get_relevant_context(last_message, "general", lang)
        specific_context = None
        if study_program != "general" and study_program != "":
            specific_context = self.weaviate_manager.get_relevant_context(last_message, study_program, lang)
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=last_message, language=lang)
        sample_questions_formatted = self.prompt_manager.format_sample_questions(sample_questions, lang)
        messages = self.prompt_manager.create_messages_with_history(general_context, specific_context, messages[-1],
                                                                    messages[:-1], sample_questions_formatted)

        return self.model.complete(messages)
