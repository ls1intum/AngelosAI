import email
import logging
from email.header import decode_header

from app.email_service.email_dto import EmailDTO


class EmailProcessor:
    def __init__(self):
        logging.info("EmailProcessor initialized")
    
    @staticmethod
    def decode_header(header_value):
        decoded_bytes, charset = decode_header(header_value)[0]
        if charset:
            return decoded_bytes.decode(charset)
        return decoded_bytes

    def process_raw_emails(self, raw_emails):
        emails = []
        for raw_email in raw_emails:
            msg = email.message_from_bytes(raw_email)
            email_data = EmailDTO.from_email_message(msg)
            email_data.body = self.get_body(msg)
            emails.append(email_data)
        logging.info("Processed %d emails", len(emails))
        return emails

    def get_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        charset = part.get_content_charset()
                        if charset is None:
                            charset = 'utf-8'  # Default to utf-8 if charset is not specified
                        try:
                            return part.get_payload(decode=True).decode(charset)
                        except UnicodeDecodeError:
                            # Handle cases where the charset might be incorrect or unsupported
                            return part.get_payload(decode=True).decode('latin1')
        else:
            charset = msg.get_content_charset()
            if charset is None:
                charset = 'utf-8'
            try:
                return msg.get_payload(decode=True).decode(charset)
            except UnicodeDecodeError:
                return msg.get_payload(decode=True).decode('latin1')
        return ""