from typing import List

from app.data.user_requests import ChatMessage
from app.managers.weaviate_manager import SampleQuestion


class PromptManager:
    def __init__(self):
        self.answer_prompt_template = """
    You are an intelligent assistant that helps the TUM School of Computation, Information and Technology's academic advising service answer questions from TUM students who want to receive detailed and accurate information about their studies.

    **Instructions:**
    - Re-read the question carefully.
    - Analyze the provided general information and, if available, study program-specific context.
    - If a provided similar question from a student is thematically very similar to the question asked, rely heavily on the respective sample answer from academic advising.
    - Else, prioritize study program-specific context over general information.
    - If no specific context is provided, base your answer solely on the general context.

    --------------------

    **Question:**
    {question}

    --------------------

    **General Information:**
    {general_context}

    --------------------

    **Study Program Specific Information:**
    {specific_context}

    --------------------

    **Similar Questions and Answers**
    To assist in crafting an accurate response, you may refer to these sample questions and answers based on similar inquiries in the past.
    {sample_questions}

    --------------------

    **Response:**
    - Be clear and concise.
    - Use a friendly and professional tone.
    - Avoid unnecessary jargon.
    - Keep the response within 200 words.

    Ensure your response is accurate, student-friendly, and directly addresses the student's concern.
    If you don't think you can answer this question only with the provided context, simply reply with:
    'False'
    """

        self.answer_prompt_template_de = """
    Sie sind ein intelligenter Assistent, der die Studienberatung der TUM School of Computation, Information and Technology hilft, Fragen von TUM-Studierenden zu beantworten, die detaillierte und genaue Informationen zu ihrem Studium erhalten wollen.

    **Anweisungen:**
    - Lesen Sie die Frage sorgfältig durch.
    - Analysieren Sie die bereitgestellten allgemeinen Informationen und, falls vorhanden, die studiengangspezifischen Informationen. Analysiere zudem, falls vorhanden die bereitgestellten ähnlichen Fragen und Antworten basierend auf früheren Anfragen.
    - Wenn eine ähnliche Frage eines Studenten thematisch sehr ähnlich zur gestellten Frage ist, stützen Sie sich stark auf die jeweilige Beispielsantwort der Studienberatung.
    - Sonst priorisieren Sie studiengangspezifische Informationen über allgemeine Informationen.
    - Wenn keine spezifischen Informationen bereitgestellt werden, basieren Sie Ihre Antwort ausschließlich auf den allgemeinen Informationen.

    **Frage:**
    {question}

    --------------------

    **Allgemeine Informationen:**
    {general_context}

    --------------------

    **Studiengangspezifische Informationen:**
    {specific_context}

    --------------------

    **Ähnliche Fragen und Antworten**
    Als Hilfestellung für eine korrekte Antwort können Sie diese Musterfragen und -antworten heranziehen, die auf ähnlichen Anfragen in der Vergangenheit basieren.
    {sample_questions}

    --------------------

    **Antwort:**
    - Seien Sie klar und prägnant.
    - Verwenden Sie einen freundlichen und professionellen Ton.
    - Vermeiden Sie unnötigen Fachjargon.
    - Halten Sie die Antwort unter 200 Wörtern.

    Stellen Sie sicher, dass Ihre Antwort genau, studierendenfreundlich und direkt auf die Frage des Studierenden eingeht.
    Wenn Sie die Frage nur mit den bereitgestellten Informationen nicht beantworten können, antworten Sie einfach mit:
    „False“
    """

        self.answer_prompt_template_with_history = """
             You are an intelligent assistant that helps the TUM School of Computation, Information and Technology's academic advising service answer questions from TUM students who want to receive detailed and accurate information about their studies.

    **Instructions:**
    - Re-read the question carefully.
    - Analyze the provided general information and, if available, study program-specific context.
    - If a provided similar question from a student is thematically very similar to the question asked, rely heavily on the respective sample answer from academic advising.
    - Else, prioritize study program-specific context over general information.
    - If no specific context is provided, base your answer solely on the general context.
    --------------------

    **Question:**
    {question}

    --------------------
    **History:**
    {history}
        

    --------------------

    **General Information:**
    {general_context}

    --------------------

    **Study Program Specific Information:**
    {specific_context}

    --------------------

    **Similar Questions and Answers**
    To assist in crafting an accurate response, you may refer to these sample questions and answers based on similar inquiries in the past.
    {sample_questions}

    --------------------

    **Response:**
    - Be clear and concise.
    - Use a friendly and professional tone.
    - Avoid unnecessary jargon.
    - Keep the response within 200 words.

    Ensure your response is accurate, student-friendly, and directly addresses the student's concern.
    If you don't think you can answer this question with the provided context, simply reply with:
    'I'm sorry for the inconvenience! But I cannot answer this question with the provided context.'
    """

    def create_messages(self, general_context: str, specific_context: str, sample_questions: str, question: str,
                        language: str):
        """Converts the template into a message format suitable for LLMs like OpenAI's GPT."""

        # Construct the system prompt
        if language == "english":
            user_content = self.answer_prompt_template.format(
                general_context=general_context,
                specific_context=specific_context or "No specific context available.",
                question=question,
                sample_questions=sample_questions
            )
            system_content = "You are an intelligent assistant that helps students of the Technical University of Munich (TUM) with questions related to their studies."

        else:
            user_content = self.answer_prompt_template_de.format(
                general_context=general_context,
                specific_context=specific_context or "Kein studienfachspezifischer Kontext verfügbar.",
                question=question,
                sample_questions=sample_questions
            )
            system_content = "Sie sind ein intelligenter Assistent, der den Studierenden der Technischen Universität München (TUM) bei Fragen rund um ihr Studium hilft"

        # Return the messages structure for the LLM
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

    def format_sample_questions(self, sample_questions: List[SampleQuestion], language: str) -> str:
        formatted_strings = []
        for sq in sample_questions:
            if language.lower() == "en":
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
    

    def create_messages_with_history(self, general_context, specific_context, question, history: List[ChatMessage],
                                     sample_questions):
        """Converts the template into a message format suitable for LLMs like OpenAI's GPT."""
        history_str = "\n\n".join(str(his) for his in history)
        # Construct the system prompt including history
        system_content = self.answer_prompt_template_with_history.format(
            history=history_str or "No prior conversation.",
            general_context=general_context,
            specific_context=specific_context or "No specific context available.",
            sample_questions=sample_questions,
            question=question
        )

        return [
            {"role": "system",
             "content": "You are an intelligent assistant that helps students of the Technical University of Munich (TUM) with questions related to their studies."},
            {"role": "user", "content": system_content}
        ]
