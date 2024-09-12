import os
import logging
import time
import traceback

from app.email_classification.email_classifier import EmailClassifier
from app.email_classification.response_service import ResponseService
from app.email_classification.study_program_classifier import StudyProgramClassifier
from app.email_service.email_client import EmailClient
from app.email_service.email_fetcher import EmailFetcher
from app.email_service.email_processor import EmailProcessor
from app.email_service.email_sender import EmailSender
from app.models.ollama_model import get_model_client


class EmailResponder:
    def __init__(self):
        self.email_client = EmailClient()
        self.email_fetcher = EmailFetcher(self.email_client)
        self.email_processor = EmailProcessor()
        self.email_sender = EmailSender(self.email_client)
        use_azure = False
        # self.model_api_key = os.getenv("LLAMA_MODEL_TOKEN")
        self.model_api_key = os.getenv("LLAMA_MODEL_TOKEN")
        self.model_url = os.getenv("LLAMA_MODEL_URI") if use_azure else os.getenv("GPU_URL")
        # self.model_url = os.getenv("LLAMA_MODEL_URI")
        self.llama = get_model_client(use_openai=use_azure, openai_api_key=self.model_api_key, model_uri=self.model_url)
        self.email_classifier = EmailClassifier(self.llama)
        self.study_program_classifier = StudyProgramClassifier(self.llama)
        self.response_service = ResponseService()
        logging.info("EmailResponder initialized")

    def start(self):
        try:
            self.email_client.connect()
            while True:
                logging.info("Fetching new emails...")
                raw_emails = self.email_fetcher.fetch_raw_emails()
                emails = self.email_processor.process_raw_emails(raw_emails)
                for email in emails:
                    classification, confidence = self.email_classifier.classify(email)
                    program_classification, program_confidence = self.study_program_classifier.classify(email)
                    self.handle_classification(email, classification, confidence, program_classification, program_confidence)
                logging.info("Sleeping for 60 seconds before next fetch")
                time.sleep(60)
        except Exception as e:
            tb = traceback.format_exc()
            logging.error("An error occurred: %s", e)
            logging.error("Traceback:\n%s", tb)
        finally:
            self.email_client.close_connections()

    def handle_classification(self, email, classification,confidence , program_classification, program_confidence):
        response_content = self.generate_email_response(email, classification)
        if classification == "non-sensitive" and confidence > 0.8:
            payload = {
                "message": response_content,
                "study_program": program_classification
            }
            self.response_service.get_response(payload)
            logging.info("api call to angelos was made")
        if response_content:
            self.email_sender.send_reply_email(original_email=email, reply_body=response_content)

    def generate_email_response(self, email, classification):
        # This method generates a response based on the classification
        response = f"Generated response for {email.subject} with classification: {classification}"
        return response


if __name__ == "__main__":
    email_responder = EmailResponder()
    email_responder.start()
