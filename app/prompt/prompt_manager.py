from langchain_core.prompts import PromptTemplate


class PromptManager:
    def __init__(self):
        self.prompt_template = """You are an assistant helping TUM students with questions about their studies.
        Your goal is to provide detailed and accurate answers to their questions.

        General information:
        {general_context}

        Specific information (if available):
        {specific_context}

        Answer the following question based on only the provided information:
        Question: {question}
        """
        self.prompt = PromptTemplate(template=self.prompt_template)

    def format_prompt(self, general_context, specific_context, question):
        return self.prompt.format(
            general_context=general_context,
            specific_context=specific_context or "No specific context available.",
            question=question
        )