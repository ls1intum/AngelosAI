from typing import List, Dict, Tuple
import re
import logging

from app.data.user_requests import ChatMessage
from app.managers.weaviate_manager import WeaviateManager
from app.models.base_model import BaseModelClient
from app.prompt.prompt_manager import PromptManager
from app.prompt.text_formatter import TextFormatter
from app.utils.language_detector import LanguageDetector
from app.post_retrieval.response_evaluator import ResponseEvaluator
from app.post_retrieval.reranker import Reranker

class RequestHandler:
    def __init__(self, weaviate_manager: WeaviateManager, reranker: Reranker, formatter: TextFormatter, model: BaseModelClient, prompt_manager: PromptManager, response_evaluator: ResponseEvaluator):
        self.weaviate_manager = weaviate_manager
        self.reranker = reranker
        self.model = model
        self.prompt_manager = prompt_manager
        self.text_formatter = formatter
        self.response_evaluator = response_evaluator
        
    GEN_THRESH = 0.25
    SPEC_THRESH = 0.35
    MAX_GENERAL = 8
    MAX_SPECIFIC = 8

    def handle_question(self, question: str, classification: str, language: str, org_id: int):
        """Handles the question by fetching relevant documents and generating an answer."""
        embedding = self.weaviate_manager.get_question_embedding(question=question)
        
        general_context_dict = self.weaviate_manager.get_relevant_context(question_embedding=embedding, study_program="general", org_id=org_id)
        
        specific_context_dict = []
        if classification != "general":
            specific_context_dict = self.weaviate_manager.get_relevant_context(question_embedding=embedding,
                                                                          study_program=classification, org_id=org_id)
        
        for x in general_context_dict:
            x['type'] = 'general'
        for x in specific_context_dict:
            x['type'] = 'specific'
        
        all_contexts = general_context_dict + specific_context_dict
        context_texts = [x['content'] for x in all_contexts]

        rerank_results = self.reranker.rerank_with_cohere(
            context_list=context_texts, query=question, language=language, top_n=len(all_contexts)
        )
        
        general_context, specific_context = self.process_and_format_contexts(all_contexts=all_contexts, rerank_results=rerank_results)
        
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=question, question_embedding=embedding, language=language, org_id=org_id)
        sample_questions_formatted = self.text_formatter.format_sample_questions(sample_questions, language)
        
        messages = self.prompt_manager.create_messages(general_context, specific_context, sample_questions_formatted,
                                                       question, language, classification)
        
        answer = self.model.complete(messages)
        logging.info(f"Answer: {answer}")
                                
        answer = self.response_evaluator.process_response(question=question, response=answer, language=language)
        logging.info(f"Answer after processing: {answer}")
                
        return answer
    
    
    def handle_chat(self, messages: List[ChatMessage], study_program: str, org_id: int, filter_by_org: bool):
        """Handles the question by fetching relevant documents and generating an answer."""
        # The last message is the user's current question
        last_message = messages[-1].message
        if study_program and study_program.lower() != "general":
            question = f"{re.sub(r'-', ' ', study_program).title()}: {last_message}"
        else:
            question = last_message
        
        last_message_embedding = self.weaviate_manager.get_question_embedding(question=question)
        chat_history_embedding = None

        # Determine language
        lang = LanguageDetector.get_language(last_message)
        
        limit = 10

        # Decide whether to retrieve context based on history
        chat_history_embedding = None
        chat_history_query = None
        if len(messages) > 2:
            chat_history_query = self.text_formatter.format_chat_history(chat_messages=messages, language=lang)
            chat_history_embedding = self.weaviate_manager.get_question_embedding(question=chat_history_query)
            limit = 8
            
        general_context_dict = self.weaviate_manager.get_relevant_context(question_embedding=last_message_embedding, study_program="general", 
                                                                        org_id=org_id, limit=limit, filter_by_org=filter_by_org)
        general_context_history_dict = []
        if chat_history_embedding is not None:
            general_context_history_dict = self.weaviate_manager.get_relevant_context(question_embedding=chat_history_embedding, study_program="general", 
                                                                            org_id=org_id, limit=limit, filter_by_org=filter_by_org)
            
        for x in general_context_dict:
            x['type'] = 'general'
        for x in general_context_history_dict:
            x['type'] = 'general'

        # Handle specific context (study program specific)
        specific_context_dict = []
        specific_context_history_dict = []
        if study_program and study_program.lower() != "general":
            specific_context_dict = self.weaviate_manager.get_relevant_context(
                question_embedding=last_message_embedding, study_program=study_program,
                org_id=org_id, limit=limit, filter_by_org=filter_by_org)
            if chat_history_embedding is not None:
                specific_context_history_dict = self.weaviate_manager.get_relevant_context(
                    question_embedding=chat_history_embedding, study_program=study_program,
                    org_id=org_id, limit=limit, filter_by_org=filter_by_org)
        for x in specific_context_dict:
            x['type'] = 'specific'
        for x in specific_context_history_dict:
            x['type'] = 'specific'

        # Combine and deduplicate all contexts
        all_contexts = (
            general_context_dict +
            general_context_history_dict +
            specific_context_dict +
            specific_context_history_dict
        )
        
        context_texts = [x['content'] for x in all_contexts]
        top_n = min(len(all_contexts), 20)

        rerank_results = self.reranker.rerank_with_cohere(
            context_list=context_texts, query=question, language=lang, top_n=top_n
        )
        
        general_context, specific_context = self.process_and_format_contexts(all_contexts=all_contexts, rerank_results=rerank_results)
        
        sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=last_message, question_embedding=last_message_embedding, language=lang, org_id=org_id)
        sample_questions_formatted = self.text_formatter.format_sample_questions(sample_questions, lang)
        
        history_formatted = self.text_formatter.format_chat_history(messages, lang)

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
    
    
    def process_and_format_contexts(self, all_contexts: List[Dict], rerank_results: List[Dict]) -> Tuple[str, str]:
        """
        Attaches rerank scores, sorts, filters, deduplicates, and formats general/specific contexts.
        Returns:
            Tuple[str, str]: (general_context, specific_context)
        """
        # Attach scores        
        for result in rerank_results:
            idx = result['index']
            score = result['relevance_score']
            all_contexts[idx]['relevance_score'] = score
            
        # Sort context based on relevance score
        all_contexts_sorted = [all_contexts[result['index']] for result in rerank_results]
        
        # Create 2 sorted lists and filter by threshold
        sorted_general = [
            x for x in all_contexts_sorted
            if x['type'] == 'general' and x.get('relevance_score', 0) >= self.GEN_THRESH
        ]

        sorted_specific = [
            x for x in all_contexts_sorted
            if x['type'] == 'specific' and x.get('relevance_score', 0) >= self.SPEC_THRESH
        ]
        # Deduplicate
        sorted_general = self.weaviate_manager.remove_exact_duplicates_from_dict(sorted_general, key='content')[:self.MAX_GENERAL]
        sorted_specific = self.weaviate_manager.remove_exact_duplicates_from_dict(sorted_specific, key='content')[:self.MAX_SPECIFIC]
        
        general_context = self.text_formatter.format_context(sorted_general)
        specific_context = self.text_formatter.format_context(sorted_specific)
        return general_context, specific_context


    # def handle_question_test_mode(self, question: str, classification: str, language: str, org_id: int):
    #     """Handles the question by fetching relevant documents and generating an answer."""
    #     embedding = self.weaviate_manager.get_question_embedding(question=question)
        
    #     general_context, general_context_list = self.weaviate_manager.get_relevant_context(question=question,
    #                                                                                        question_embedding=embedding,
    #                                                                                        study_program="general",
    #                                                                                        language=language,
    #                                                                                        org_id=org_id,
    #                                                                                        test_mode=True)
    #     specific_context = None
    #     if classification != "general":
    #         specific_context, specific_context_list = self.weaviate_manager.get_relevant_context(question=question,
    #                                                                                              question_embedding=embedding,
    #                                                                                              study_program=classification,
    #                                                                                              language=language,
    #                                                                                              org_id=org_id,
    #                                                                                              test_mode=True)
    #     else:
    #         specific_context_list = []
    #     sample_questions = self.weaviate_manager.get_relevant_sample_questions(question=question, question_embedding=embedding, language=language, org_id=org_id)
    #     sample_questions_formatted = self.prompt_manager.format_sample_questions(sample_questions, language)
    #     sample_questions_context_list = self.prompt_manager.format_sample_questions_test_mode(sample_questions=sample_questions, language=language)
    #     messages = self.prompt_manager.create_messages(general_context, specific_context, sample_questions_formatted,
    #                                                    question, language, classification)
    #     answer, tokens = self.model.complete_with_tokens(messages)
        
    #     answer = self.response_evaluator.process_response(question=question, response=answer, language=language)
        
    #     return answer, tokens, general_context_list, specific_context_list, sample_questions_context_list