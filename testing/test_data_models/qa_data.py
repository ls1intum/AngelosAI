from typing import List

class QAData:
    def __init__(self, question: str, answer: str, language: str, classification: str, label: str):
        """
        Initializes the QAData object with the given attributes.

        :param question: The question asked by the student.
        :param answer: The answer provided to the student.
        :param key_facts: A list of key facts that should be included in the answer.
        :param expected_sources: A list of expected sources such as URLs or document references.
        """
        self.question = question
        self.answer = answer
        self.classification = classification
        self.label = label
        self.language = language

    def __repr__(self):
        """
        String representation for easy debugging.
        """
        return (f"QAData(label='{self.label}' question='{self.question}', answer='{self.answer}', language='{self.language}', classification='{self.classification}')")