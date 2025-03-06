import logging

import requests

from app.common.environment import config


class ResponseService:
    def __init__(self):
        self.angelos_url = config.ANGELOS_URL
        self.api_url = f"{self.angelos_url}/mail/ask"
        self.session = requests.Session()
        self.api_key = config.ANGELOS_APP_API_KEY
        self._set_authorization_header()

    def _set_authorization_header(self):
        """Helper function to set the authorization header."""
        self.headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

    def get_response(self, payload, sender_email):
        """Send a request to the API endpoint with the given payload."""
        try:
            headers = self.headers.copy()
            headers["X-Sender-Email"] = sender_email 
            response = self.session.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            logging.error(f"An error occurred: {err}")
            raise
