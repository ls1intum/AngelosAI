import re
from typing import List, Dict

from app.data.user_requests import ChatMessage
from app.managers.weaviate_manager import SampleQuestion

FALLBACK_MESSAGES = {
    3: {
        "en": (
            "Unfortunately, I cannot assist you with this inquiry. "
            "Please contact the ASA (School Office Heilbronn) for program-specific questions: "
            "[ASA (School Office Heilbronn)](https://www.cit.tum.de/en/cit/studies/degree-programs/master-information-engineering/consultation-contact/). "
            "For general questions about studying at TUM, admissions and enrollment, please contact the CST: "
            "[TUM Center for Study and Teaching (CST)](https://www.tum.de/en/studies/tum-center-for-study-and-teaching). "
            "Thank you!"
        ),
        "de": (
            "Leider kann ich Ihnen bei dieser Anfrage nicht weiterhelfen. "
            "Bitte wenden Sie sich bei programmspezifischen Fragen an das ASA (School Office Heilbronn): "
            "[ASA (School Office Heilbronn)](https://www.cit.tum.de/cit/studium/studiengaenge/bachelor-information-engineering/beratung-kontakt/). "
            "Bei allgemeinen Fragen zum Studium an der TUM sowie zu Bewerbung, Zulassung und Immatrikulation wenden Sie sich bitte an das CST: "
            "[TUM Center for Study and Teaching (CST)](https://www.tum.de/studium/tumcst). "
            "Vielen Dank!"
        ),
    },
    "default": {
        "en": (
            "I'm sorry, but I cannot answer this question based on the available information. "
            "In this case, please contact the advising team responsible for your degree program or the CST "
            "(Central Study Team) at TUM."
        ),
        "de": (
            "Es tut mir leid, aber ich kann diese Frage basierend auf den vorliegenden Informationen nicht beantworten. "
            "Bitte wenden Sie sich in diesem Fall direkt an das für den Studiengang zuständige Studienberatungs-Team "
            "oder das CST (Central Study Team) der TUM."
        ),
    },
}

class TextFormatter:
    def format_context(self, context_dicts: List[Dict]):
        """
        Formats a list of context dictionaries into a string with links and content.

        Args:
            context_dicts (List[Dict]): List of dicts with 'link' and 'content' keys.

        Returns:
            str: Formatted context string.
        """
        formatted = []
        for doc in context_dicts:
            link_str = f'Link: {doc["link"]}' if doc.get("link") else 'Link: -'
            formatted.append(f'{link_str}\nContent: {doc["content"]}')
        return "\n-----\n".join(formatted)
    
    def format_sample_questions(self, sample_questions: List[SampleQuestion], language: str) -> str:
        formatted_strings = []
        for sq in sample_questions:
            if language.lower() == "english":
                formatted_string = f"""
    Topic: {sq.topic}
    Student: "{sq.question}"
    Academic Advising: "{sq.answer}"
    """.strip()
            else:
                formatted_string = f"""
    Thema: {sq.topic}
    Student: "{sq.question}"
    Studienberatung: "{sq.answer}"
    """.strip()
            formatted_strings.append(formatted_string)
        combined_string = "\n-----\n".join(formatted_strings)
        return combined_string

    def format_chat_history(self, chat_messages: List[ChatMessage], language: str) -> str:
        # Determine labels based on language
        if language.lower() == "english":
            advisor_label = "TUM AI Assistant"
            student_label = "Student"
        else:
            advisor_label = "TUM KI Assistent"
            student_label = "Student"

        # Format messages
        formatted_strings = []
        for cm in chat_messages:
            sender = student_label if cm.type.lower() == "user" else advisor_label
            formatted_string = f'{sender}: "{cm.message.strip()}"'
            formatted_strings.append(formatted_string)

        # Join formatted messages with separator
        combined_string = "\n\n".join(formatted_strings)
        return combined_string

    # Format the study program
    def format_study_program(self, study_program: str, language: str) -> str:
        if not study_program or study_program.lower() == "general":
            return "No study program specified" if language.lower() == "english" else "Kein Studiengang angegeben"

        # Capitalize first letter of each word and replace hyphens with spaces
        formatted_program = re.sub(r'-', ' ', study_program).title()

        if language.lower() == "english":
            return f"The study program of the student is {formatted_program}"
        else:
            return f"Der Studiengang des Studenten ist {formatted_program}"

    def format_sample_questions_test_mode(self, sample_questions: List[SampleQuestion], language: str) -> List[str]:
        formatted_strings = []
        for sq in sample_questions:
            if language.lower() == "english":
                formatted_string = f"""
    Topic: {sq.topic}
    Student: "{sq.question}"
    Academic Advising: "{sq.answer}"
    """.strip()
            else:
                formatted_string = f"""
    Thema: {sq.topic}
    Student: "{sq.question}"
    Studienberatung: "{sq.answer}"
    """.strip()
            formatted_strings.append(formatted_string)
        return formatted_strings

    def build_chat_query(self, messages: List[ChatMessage], study_program: str, num_messages: int = 3) -> str:
        """
        Builds a query string from the last num_messages user messages.

        Args:
            messages (List[ChatMessage]): The list of chat messages.
            num_messages (int): The number of recent user messages to include.

        Returns:
            str: The concatenated query string.
        """
        # Extract messages of type 'user'
        user_messages = [msg.message for msg in messages if msg.type == 'user']
        # Take the last num_messages
        recent_user_messages = user_messages[-num_messages:]
        # Concatenate them into one query string
        query = " ".join(recent_user_messages)
        # Integrate study program
        formatted_program = re.sub(r'-', ' ', study_program).title()
        query_with_program = f"{formatted_program}: {query}"
        return query_with_program
    
    def get_fallback_message(self, org_id: int, language: str) -> str:
        lang = self.normalize_lang(language)
        per_org = FALLBACK_MESSAGES.get(org_id)
        if per_org and lang in per_org:
            return per_org[lang]
        return FALLBACK_MESSAGES["default"][lang]
    
    def normalize_lang(self, language: str) -> str:
        """Return 'en' or 'de'."""
        if not language:
            return "en"
        l = language.lower()
        if l.startswith("de") or "german" in l or "deutsch" in l:
            return "de"
        return "en"