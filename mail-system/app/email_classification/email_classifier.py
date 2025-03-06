import json
import logging
import os

from typing import List

from app.common.environment import config
from app.common.text_cleaner import TextCleaner
from app.email_classification.classifier import Classifier
from app.email_service.email_dto import EmailDTO
from app.models.ollama_model import BaseModelClient
from app.prompts.classification_prompts import generate_classification_prompt


class EmailClassifier(Classifier):
    def __init__(self, model: BaseModelClient, study_programs: List[str] = None):
        """
        :param model: LLM or classification model
        :param study_programs: A list of study programs for a given organization
        """
        super().__init__(model)
        self.study_programs = study_programs or []
        logging.info(f"EmailClassifier initialized with {len(self.study_programs)} study programs.")

    def classify(self, email: EmailDTO):
        """
        Uses the LLM to classify an email into:
        1) non-sensitive / sensitive
        2) language
        3) matched study program (from self.study_programs)
        """
        logging.info("Classifying email...")
        cleansed_text = TextCleaner.cleanse_text(email.body)
        study_programs_str = ", ".join(self.study_programs)
        
        # Generate a prompt that includes these study programs
        prompt = generate_classification_prompt(
            body=cleansed_text, 
            subject=email.subject,
            study_programs=study_programs_str
        )
        result = self.request_llm(prompt)
        return self.parse_classification_result(result)

    @staticmethod
    def parse_classification_result(result):
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError as e:
            # Fallback: if JSON parsing fails, attempt to remove markdown code fences
            result_clean = result.strip()
            if result_clean.startswith("```"):
                lines = result_clean.splitlines()
                lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                result_clean = "\n".join(lines)
            # Try parsing again
            parsed_result = json.loads(result_clean)
        classification = parsed_result.get("classification", "").lower()
        language = parsed_result.get("language", "").lower()
        study_program = parsed_result.get("study_program", "").lower()
        logging.info(f"Classified as: {classification}, language: {language}, study_program: {study_program}")
        return classification, language, study_program