import threading
import logging
from typing import Dict, Tuple, List

from app.email_responder.email_responder import EmailResponder

class ThreadManager:
    """
    Tracks threads keyed by org_id. Each thread runs an EmailResponder that polls email.
    """
    def __init__(self):
        # org_id -> (thread, responder)
        self._threads: Dict[int, Tuple[threading.Thread, EmailResponder]] = {}

    def start_thread(self, org_id: int, mail_account: str, mail_password: str, study_programs: List[str]) -> threading.Event:
        """
        Create and start a thread for an org if not already running.
        Returns True if newly started, False if it was already running.
        """
        if org_id in self._threads:
            # Already running
            logging.info(f"Thread for org_id={org_id} already exists.")
            _, responder = self._threads[org_id]
            return responder._status_event
        
        # Start event
        status_event = threading.Event()
        
        responder = EmailResponder(mail_account=mail_account, mail_password=mail_password, org_id=org_id, status_event=status_event, study_programs=study_programs)

        t = threading.Thread(target=responder.start_polling, daemon=True)
        self._threads[org_id] = (t, responder)
        t.start()
        logging.info(f"Started email polling thread for org_id={org_id}")
        return status_event

    def stop_thread(self, org_id: int) -> bool:
        """
        Stop the thread if it exists. Return True if successfully stopped, False if not running.
        """
        if org_id not in self._threads:
            logging.info(f"No thread found for org_id={org_id} to stop.")
            return False

        thread, responder = self._threads[org_id]
        responder.stop_polling()
        thread.join(timeout=10)
        del self._threads[org_id]
        logging.info(f"Stopped thread for org_id={org_id}")
        return True

    def update_credentials(self, org_id: int, mail_account: str, mail_password: str):
        """
        Update credentials on a running responder. 
        If no thread is running, you might decide to start one or do nothing.
        """
        if org_id in self._threads:
            _, responder = self._threads[org_id]
            responder.set_credentials(mail_account, mail_password)
        else:
            logging.info(f"update_credentials called but no thread for org_id={org_id}")

    def get_status(self, org_id: int) -> str:
        """
        Returns the in-memory status from the EmailResponder if running, else 'INACTIVE'.
        """
        if org_id not in self._threads:
            return "INACTIVE"
        _, responder = self._threads[org_id]
        return responder.get_status()

    def stop_all(self):
        """
        Gracefully stop all threads, e.g. on shutdown.
        """
        for org_id in list(self._threads.keys()):
            self.stop_thread(org_id)

thread_manager = ThreadManager()