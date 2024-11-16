from typing import List
import re

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
                                                       question, language, classification)

        return self.model.complete(messages)

    def handle_question_test_mode(self, question: str, classification: str, language: str):
        """Handles the question by fetching relevant documents and generating an answer."""
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
                                                       question, language, classification)
        answer, tokens = self.model.complete_with_tokens(messages)
        return answer, tokens, general_context_list, specific_context_list
    
    def handle_chat(self, messages: List[ChatMessage], study_program: str):
        """Handles the question by fetching relevant documents and generating an answer."""
        # The last message is the user's current question
        last_message = messages[-1].message

        # Determine language
        lang = LanguageDetector.get_language(last_message)

        # Decide whether to retrieve context based on history
        if len(messages) <= 2:
            get_history_context = False
            general_query = f"{re.sub(r'-', ' ', study_program).title()}: {last_message}"
            context_limit = 10
            context_top_n = 5
        else:
            get_history_context = True
            general_query = last_message
            context_limit = 8
            context_top_n = 4

        # Retrieve general context based on the last message
        general_context_last = self.weaviate_manager.get_relevant_context(
            general_query, "general", lang, limit=context_limit, top_n=context_top_n
        )
        general_context = general_context_last

        # If applicable, retrieve additional context based on history
        if get_history_context:
            # Build a query from the chat history
            chat_query = self.prompt_manager.build_chat_query(messages, study_program, num_messages=3)

            # Retrieve general context using the chat history
            general_context_history = self.weaviate_manager.get_relevant_context(
                chat_query, "general", lang, limit=4, top_n=2
            )
            # Combine the contexts
            general_context = f"{general_context_last}\n-----\n{general_context_history}"

        # Retrieve specific context if a study program is specified
        specific_context = None
        if study_program and study_program.lower() != "general":
            # Retrieve specific context based on the last message
            specific_context_last = self.weaviate_manager.get_relevant_context(
                last_message, study_program, lang, limit=context_limit, top_n=context_top_n
            )
            specific_context = specific_context_last

            if get_history_context:
                # Retrieve specific context using the chat history
                specific_context_history = self.weaviate_manager.get_relevant_context(
                    chat_query, study_program, lang, limit=4, top_n=2
                )
                # Combine the contexts
                specific_context = f"{specific_context_last}\n-----\n{specific_context_history}"

        # Retrieve and format sample questions
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(
            question=last_message, language=lang
        )
        sample_questions_formatted = self.prompt_manager.format_sample_questions(
            sample_questions, lang
        )

        # Format chat history (excluding the last message)
        if len(messages) > 1:
            history_formatted = self.prompt_manager.format_chat_history(messages, lang)
        else:
            history_formatted = None  # No history to format

        # Create messages for the model
        messages_to_model = self.prompt_manager.create_messages_with_history(
            general_context=general_context,
            specific_context=specific_context,
            question=last_message,
            history=history_formatted,
            sample_questions=sample_questions_formatted,
            language=lang,
            study_program=study_program
        )

        # Generate and return the answer
        return self.model.complete(messages_to_model)
    
    def add_document(self, question: str, classification: str):
        return self.weaviate_manager.add_document(question, classification)
