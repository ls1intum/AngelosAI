import datetime
import logging
import threading
import time
import traceback
from typing import List

from app.email_classification.email_classifier import EmailClassifier
from app.email_responder.response_service import ResponseService
from app.email_service.email_client import EmailClient
from app.email_service.email_processor import EmailProcessor
from app.email_service.email_service import EmailService
from app.models.model_loader import get_model_client


class EmailResponder:
    def __init__(self, mail_account: str, mail_password: str, org_id: int, status_event: threading.Event = None,
                 study_programs: List[str] = None):
        self.org_id = org_id
        self._status_event = status_event
        self.email_client = EmailClient(email=mail_account, password=mail_password)
        self.email_processor = EmailProcessor()
        self.email_service = EmailService(self.email_client, 3)
        self.llama = get_model_client()
        self.email_classifier = EmailClassifier(self.llama, study_programs)
        self.response_service = ResponseService()

        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 2
        self._running = False
        self._lock = threading.Lock()
        self._current_status = "INACTIVE"  # or 'ACTIVE', 'ERROR'

        logging.info("EmailResponder initialized")

    def set_credentials(self, username, password):
        with self._lock:
            self.email_client.username = username
            self.email_client.password = password

    def start_polling(self):
        with self._lock:
            if self._running:
                logging.info("Responder is already running.")
                return
            self._running = True
            self._current_status = "ACTIVE"
            self._poll_start_time = datetime.datetime.now()

        # Attempt initial connect
        try:
            self.email_client.connect()
        except Exception as e:
            logging.error(f"Initial mail client connect failed: {e}")
            self._set_status("ERROR")
            self._running = False

            # Signal that the initial connect attempt has completed
            if self._status_event:
                self._status_event.set()
            return

        if self._status_event:
            self._status_event.set()

        # Main loop
        try:
            while self._is_running():
                logging.info("Fetching new emails...")
                raw_emails = self.email_service.fetch_raw_emails(since=self._poll_start_time)
                if not raw_emails:
                    time.sleep(30)
                    continue
                emails = self.email_processor.process_raw_emails(raw_emails)
                for email in emails:
                    if email.in_reply_to is None and len(email.references) == 0 and (
                            email.spam == "NO" or email.spam is None):
                        try:
                            classification, language, study_program = self.classify_with_retries(email)
                        except Exception as e:
                            logging.error("Classification failed for email %s: %s", email, e)
                            # Optionally flag the email or handle it differently
                            self.email_service.flag_email(email.message_id)
                            # Continue processing the next email
                            continue
                        self.handle_classification(email, classification, study_program, language)
                    else:
                        self.email_service.flag_email(email.message_id)
                time.sleep(60)

        except Exception as e:
            tb = traceback.format_exc()
            logging.error("An error occurred in EmailResponder: %s", e)
            logging.error("Traceback:\n%s", tb)
            self._set_status("ERROR")

        finally:
            self.email_client.close_connections()
            with self._lock:
                self._running = False
                if self._current_status != "ERROR":
                    self._current_status = "INACTIVE"

    def stop_polling(self):
        with self._lock:
            self._running = False
            if self._current_status != "ERROR":
                self._current_status = "INACTIVE"

    def _is_running(self):
        with self._lock:
            return self._running

    def get_status(self):
        with self._lock:
            return self._current_status

    def _set_status(self, status):
        with self._lock:
            self._current_status = status

    def handle_classification(self, email, classification, study_program, language):
        try:
            response_content = None
            if classification.strip().lower() == "non-sensitive":
                payload = {
                    "org_id": self.org_id,
                    "message": email.body,
                    "study_program": study_program,
                    "language": language,
                }
                response_content = self.response_service.get_response(payload, sender_email=email.from_address)
            if response_content and response_content['answer'] != "False":
                self.email_service.send_reply_email(original_email=email, reply_body=response_content['answer'])
            else:
                logging.info(
                    f"No proper answer can be found: {response_content and response_content['answer'] == "False"} or it is classified as sensitive")
                self.email_service.flag_email(email.message_id)
        except Exception as e:
            logging.error("Failed to send email response: %s", e)
            self.email_service.flag_email(email.message_id)

    def classify_with_retries(self, email):
        """Attempts to classify an email with retries."""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return self.email_classifier.classify(email)
            except Exception as e:
                tb = traceback.format_exc()
                logging.error("Error on attempt %d for email: %s", attempt, email)
                logging.error("An error occurred: %s", e)
                logging.error("Traceback:\n%s", tb)

                # If max retries reached, raise the exception
                if attempt == self.MAX_RETRIES:
                    logging.error("Max retries reached for email: %s. Skipping this email.", email)
                    raise
                else:
                    logging.info("Retrying... (attempt %d of %d)", attempt, self.MAX_RETRIES)
                    time.sleep(self.RETRY_DELAY)
