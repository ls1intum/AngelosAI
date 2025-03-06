import imaplib
import logging
import smtplib
import time

from app.common.environment import config


class EmailClient:
    def __init__(self, email: str, password: str):
        self.username = email
        self.password = password
        self.imap_server = config.IMAP_SERVER
        self.smtp_server = config.SMTP_SERVER
        self.imap_port = int(config.IMAP_PORT)
        self.smtp_port = int(config.SMTP_PORT)
        self.imap_connection = None
        self.smtp_connection = None
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        logging.info("EmailClient initialized")

    def get_imap_connection(self):
        if not self.imap_connection and not self.is_imap_connection_alive():
            self.connect_imap()
        return self.imap_connection

    def get_smtp_connection(self):
        if not self.smtp_connection and not self.is_smtp_connection_alive():
            self.connect_smtp()
        return self.smtp_connection

    def connect_imap(self):
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logging.info("Connecting to IMAP server...")
                self.imap_connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
                self.imap_connection.login(self.username, self.password)
                logging.info("Connected to IMAP server.")
                return
            except imaplib.IMAP4.error as e:
                logging.error("IMAP connection error on attempt %d: %s", attempt, e)
                self.imap_connection = None
                time.sleep(self.RETRY_DELAY)

        logging.error("Failed to connect to IMAP server after %d attempts.", self.MAX_RETRIES)
        raise ConnectionError("Could not establish an IMAP connection.")

    def connect_smtp(self):
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logging.info("Connecting to SMTP server...")
                self.smtp_connection = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                self.smtp_connection.login(self.username, self.password)
                logging.info("Connected to SMTP server.")
                return
            except smtplib.SMTPException as e:
                logging.error("SMTP connection error on attempt %d: %s", attempt, e)
                self.smtp_connection = None
                time.sleep(self.RETRY_DELAY)

        logging.error("Failed to connect to SMTP server after %d attempts.")
        raise ConnectionError("Could not establish an SMTP connection.")

    def close_connections(self):
        if self.imap_connection:
            self.imap_connection.logout()
            self.imap_connection = None
            logging.info("IMAP connection closed")
        if self.smtp_connection:
            self.smtp_connection.quit()
            self.smtp_connection = None
            logging.info("SMTP connection closed")

    def connect(self):
        self.connect_imap()
        self.connect_smtp()
        
    def reconnect_imap(self):
        logging.info("Reconnecting to IMAP server...")
        if self.imap_connection:
            try:
                self.imap_connection.logout()
            except Exception as e:
                logging.error("Error during IMAP logout in reconnect: %s", e)
            finally:
                self.imap_connection = None
        self.connect_imap()

    def is_smtp_connection_alive(self):
        try:
            # The noop() method returns a tuple (code, message)
            code, _ = self.smtp_connection.noop()
            return code == 250
        except Exception as e:
            logging.info("SMTP connection is not alive: %s", e)
            return False

    def is_imap_connection_alive(self):
        try:
            # The noop() method returns a tuple (code, message)
            code, _ = self.imap_connection.noop()
            return code == "OK"
        except Exception as e:
            logging.info("IMAP connection is not alive: %s", e)
            return False
