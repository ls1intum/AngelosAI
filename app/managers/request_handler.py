from typing import List
import re
import logging

from app.data.user_requests import ChatMessage
from app.managers.weaviate_manager import WeaviateManager
from app.models.base_model import BaseModelClient
from app.prompt.prompt_manager import PromptManager
from app.utils.language_detector import LanguageDetector
from app.post_retrieval.response_evaluator import ResponseEvaluator


class RequestHandler:
    def __init__(self, weaviate_manager: WeaviateManager, model: BaseModelClient, prompt_manager: PromptManager, response_evaluator: ResponseEvaluator):
        self.weaviate_manager = weaviate_manager
        self.model = model
        self.prompt_manager = prompt_manager
        self.response_evaluator = response_evaluator

    def handle_question(self, question: str, classification: str, language: str, org_id: int):
        """Handles the question by fetching relevant documents and generating an answer."""
        logging.info("Handle question...")
        embedding = self.weaviate_manager.get_question_embedding(question=question)
        
        general_context = self.weaviate_manager.get_relevant_context(question=question, question_embedding=embedding, study_program="general",
                                                                     language=language, org_id=org_id)
        specific_context = None
        if classification != "general":
            specific_context = self.weaviate_manager.get_relevant_context(question=question,
                                                                          question_embedding=embedding,
                                                                          study_program=classification,
                                                                          language=language,
                                                                          org_id=org_id)
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=question, question_embedding=embedding, language=language, org_id=org_id)
        sample_questions_formatted = self.prompt_manager.format_sample_questions(sample_questions, language)
        messages = self.prompt_manager.create_messages(general_context, specific_context, sample_questions_formatted,
                                                       question, language, classification)
        
        answer = self.model.complete(messages)
                                
        answer = self.response_evaluator.process_response(question=question, response=answer, language=language)
                
        return answer

    def handle_question_test_mode(self, question: str, classification: str, language: str, org_id: int):
        """Handles the question by fetching relevant documents and generating an answer."""
        embedding = self.weaviate_manager.get_question_embedding(question=question)
        
        general_context, general_context_list = self.weaviate_manager.get_relevant_context(question=question,
                                                                                           question_embedding=embedding,
                                                                                           study_program="general",
                                                                                           language=language,
                                                                                           org_id=org_id,
                                                                                           test_mode=True)
        specific_context = None
        if classification != "general":
            specific_context, specific_context_list = self.weaviate_manager.get_relevant_context(question=question,
                                                                                                 question_embedding=embedding,
                                                                                                 study_program=classification,
                                                                                                 language=language,
                                                                                                 org_id=org_id,
                                                                                                 test_mode=True)
        else:
            specific_context_list = []
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=question, question_embedding=embedding, language=language, org_id=org_id)
        sample_questions_formatted = self.prompt_manager.format_sample_questions(sample_questions, language)
        sample_questions_context_list = self.prompt_manager.format_sample_questions_test_mode(sample_questions=sample_questions, language=language)
        messages = self.prompt_manager.create_messages(general_context, specific_context, sample_questions_formatted,
                                                       question, language, classification)
        answer, tokens = self.model.complete_with_tokens(messages)
        
        answer = self.response_evaluator.process_response(question=question, response=answer, language=language)
        
        return answer, tokens, general_context_list, specific_context_list, sample_questions_context_list
    
    def handle_chat(self, messages: List[ChatMessage], study_program: str, org_id: int, filter_by_org: bool):
        """Handles the question by fetching relevant documents and generating an answer."""
        # The last message is the user's current question
        last_message = messages[-1].message
        
        last_message_embedding = self.weaviate_manager.get_question_embedding(question=last_message)

        # Determine language
        lang = LanguageDetector.get_language(last_message)

        # Decide whether to retrieve context based on history
        if len(messages) <= 2:
            get_history_context = False
            general_query = f"{re.sub(r'-', ' ', study_program).title()}: {last_message}"
            general_query_embedding = self.weaviate_manager.get_question_embedding(question=general_query)
            context_limit = 10
            context_top_n = 5
            
        else:
            get_history_context = True
            general_query = last_message
            general_query_embedding = last_message_embedding
            context_limit = 8
            context_top_n = 4

        # Retrieve general context based on the last message
        general_context_last = self.weaviate_manager.get_relevant_context(
            question=general_query, question_embedding=general_query_embedding, study_program="general", 
            language=lang, limit=context_limit, top_n=context_top_n, org_id=org_id, filter_by_org=filter_by_org
        )
        general_context = general_context_last

        # If applicable, retrieve additional context based on history
        if get_history_context:
            # Build a query from the chat history
            chat_query = self.prompt_manager.build_chat_query(messages, study_program, num_messages=3)
            
            chat_query_embedding = self.weaviate_manager.get_question_embedding(question=chat_query)

            # Retrieve general context using the chat history
            general_context_history = self.weaviate_manager.get_relevant_context(
                question=chat_query, question_embedding=chat_query_embedding, study_program="general", 
                language=lang, limit=4, top_n=2, org_id=org_id, filter_by_org=filter_by_org
            )
            # Combine the contexts
            general_context = f"{general_context_last}\n-----\n{general_context_history}"

        # Retrieve specific context if a study program is specified
        specific_context = None
        if study_program and study_program.lower() != "general":
            # Retrieve specific context based on the last message
            specific_context_last = self.weaviate_manager.get_relevant_context(
                question=last_message, question_embedding=last_message_embedding, study_program=study_program, 
                language=lang, limit=context_limit, top_n=context_top_n, org_id=org_id, filter_by_org=filter_by_org
            )
            specific_context = specific_context_last

            if get_history_context:
                # Retrieve specific context using the chat history
                specific_context_history = self.weaviate_manager.get_relevant_context(
                    question=chat_query, question_embedding=chat_query_embedding, study_program=study_program,
                    language=lang, limit=4, top_n=2, org_id=org_id, filter_by_org=filter_by_org
                )
                # Combine the contexts
                specific_context = f"{specific_context_last}\n-----\n{specific_context_history}"

        # Retrieve and format sample questions
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(
            question=last_message, question_embedding=last_message_embedding, language=lang, org_id=org_id
        )
        sample_questions_formatted = self.prompt_manager.format_sample_questions(
            sample_questions=sample_questions, language=lang
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

