import logging
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.email_service.email_dto import EmailDTO, InboxType

class EmailService:
    def __init__(self, email_client, retries):
        self.email_client = email_client
        self.max_retries = retries

    def fetch_raw_emails(self, folder="inbox", since=None):
        logging.info("EmailFetcher fetching raw emails from folder: %s", folder)
        for attempt in range(1, self.max_retries + 1):
            try:
                connection = self.email_client.get_imap_connection()
                connection.select(folder)

                criteria = []
                if since:
                    date_str = since.strftime("%d-%b-%Y")
                    criteria.extend(['SINCE', date_str])
                
                criteria.extend([InboxType.Unseen.value, InboxType.Unflagged.value])
                
                status, messages = connection.search(None, *criteria)
                
                email_ids = messages[0].split()
                raw_emails = []
                for email_id in email_ids:
                    res, msg = connection.fetch(email_id, "(RFC822)")
                    for response_part in msg:
                        if isinstance(response_part, tuple):
                            raw_emails.append(response_part[1])
                logging.info("EmailFetcher fetched %d raw emails", len(raw_emails))
                return raw_emails
            except Exception as e:
                logging.error("Error fetching raw emails (attempt %d/%d): %s", attempt, self.max_retries, e)
                try:
                    self.email_client.reconnect_imap()
                except Exception as recon_err:
                    logging.error("Reconnection failed: %s", recon_err)
                time.sleep(3)
        logging.error("Max retries reached. Skipping email fetch for now.")
        return []

    def search_by_message_id(self, message_id):
        imap_conn = self.email_client.get_imap_connection()
        imap_conn.select('inbox')
        logging.info(f"Searching for message with ID: {message_id}...")

        result, data = imap_conn.uid('SEARCH', None, f'(HEADER Message-ID "{message_id}")')

        if result == 'OK':
            email_uids = data[0].split()
            if email_uids:
                logging.info(f"Found email with UID: {email_uids[-1]}")
                return email_uids[-1]
            else:
                logging.warning(f"No email found with Message-ID: {message_id}")
                return None
        else:
            logging.error(f"Search failed for Message-ID: {message_id}")
            return None

    def flag_email(self, message_id):
        email_uid = self.search_by_message_id(message_id)
        if email_uid:
            # Set both \Flagged and \Unseen flags
            imap_conn = self.email_client.get_imap_connection()

            result, response = imap_conn.uid('STORE', email_uid, '+FLAGS', r'(\Flagged \Seen)')

            if result == 'OK':
                # Now remove the \Seen flag to keep it unread
                imap_conn.uid('STORE', email_uid, '-FLAGS', r'(\Seen)')
                logging.info(f"Email with UID {email_uid} has been successfully flagged and set to unread.")
            else:
                logging.error(f"Failed to flag the email with UID {email_uid}.")
        else:
            logging.error("Invalid UID. No email to flag.")

    def send_reply_email(self, original_email: EmailDTO, reply_body):
        smtp_conn = self.email_client.get_smtp_connection()

        # Extract headers from the original email
        from_address = original_email.from_address
        to_address = self.email_client.username
        subject = "Re: " + original_email.subject
        message_id = original_email.message_id

        # Create the reply email
        msg = MIMEMultipart()
        msg['From'] = to_address
        msg['To'] = from_address
        msg['Subject'] = subject
        msg['In-Reply-To'] = message_id
        msg['References'] = message_id
        # Attach the reply body
        msg.attach(MIMEText(reply_body, 'plain'))

        try:
            smtp_conn.send_message(msg)
            logging.info("Reply email sent to %s", from_address)
        except (smtplib.SMTPException, ConnectionError) as e:
            logging.error("Failed to send email due to %s. Attempting to reconnect and resend.", e)
            try:
                # Attempt to reconnect
                self.email_client.connect_smtp()
                smtp_conn = self.email_client.get_smtp_connection()
                smtp_conn.send_message(msg)
                logging.info("Reply email re-sent to %s", from_address)
            except Exception as e2:
                logging.error("Resend attempt failed: %s", e2)
                raise
