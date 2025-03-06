import enum
from dataclasses import dataclass, field
from email import header
from email.message import Message
from typing import List, Optional


class InboxType(enum.Enum):
    All = 'ALL'
    Unseen = 'UNSEEN'
    Unflagged = 'UNFLAGGED'


@dataclass
class EmailDTO:
    delivered_to: Optional[str] = None
    received_by: List[str] = field(default_factory=list)
    received_date_time: List[str] = field(default_factory=list)
    return_path: Optional[str] = None
    received_spf: Optional[str] = None
    from_address: Optional[str] = None
    content_type: Optional[str] = None
    charset: Optional[str] = None
    content_transfer_encoding: Optional[str] = None
    subject: Optional[str] = None
    message_id: Optional[str] = None
    date: Optional[str] = None
    to: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: List[str] = field(default_factory=list)
    spam: Optional[str] = None
    body: Optional[str] = None
    sensitive: Optional[bool] = True

    @classmethod
    def from_email_message(cls, msg: Message):
        headers = {key.lower(): msg.get_all(key) for key in msg.keys()}

        email_data = {
            "delivered_to": headers.get("delivered-to", [None])[0],
            "received_by": headers.get("received", []),
            "received_date_time": headers.get("received", []),
            "return_path": headers.get("return-path", [None])[0],
            "from_address": headers.get("from", [None])[0],
            "content_type": msg.get_content_type(),
            "charset": msg.get_content_charset(),
            "content_transfer_encoding": headers.get("content-transfer-encoding", [None])[0],
            "subject": cls.decode_email_subject(headers.get("subject", [None])[0]),
            "message_id": headers.get("message-id", [None])[0],
            "date": headers.get("date", [None])[0],
            "to": headers.get("to", [None])[0],
            "in_reply_to": headers.get("in-reply-to", [None])[0],
            "references": headers.get("references", []),
            "spam": headers.get("x-spam-flag", [None])[0],
        }
        return cls(**email_data)

    @staticmethod
    def decode_email_subject(encoded_subject):
        # Decode the subject using email.header
        decoded_fragments = header.decode_header(encoded_subject)

        # Join decoded parts together, converting bytes to strings if necessary
        decoded_subject = ''.join(
            part.decode(encoding if encoding else 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decoded_fragments
        )
        return decoded_subject

    @classmethod
    def from_dict(cls, data: dict):
        filtered_data = {key: value for key, value in data.items() if key in cls.__annotations__}
        return cls(**filtered_data)
