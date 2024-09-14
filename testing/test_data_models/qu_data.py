class QAData:
    def __init__(self, question: str, answer: str, key_facts: list, expected_sources: list, study_program: str, label: str):
        """
        Initializes the QAData object with the given attributes.

        :param question: The question asked by the student.
        :param answer: The answer provided to the student.
        :param key_facts: A list of key facts that should be included in the answer.
        :param expected_sources: A list of expected sources such as URLs or document references.
        """
        self.question = question
        self.answer = answer
        self.key_facts = key_facts
        self.expected_sources = expected_sources
        self.classification = study_program
        self.label = label

    def __repr__(self):
        """
        String representation for easy debugging.
        """
        return (f"QAData(label='{self.label}' question='{self.question}', answer='{self.answer}', "
                f"key_facts={self.key_facts}, expected_sources={self.expected_sources}, classification='{self.classification}')")