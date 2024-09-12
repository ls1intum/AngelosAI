from langchain_core.prompts import PromptTemplate


class PromptManager:
    def __init__(self):
        self.prompt_template = """
    You are an intelligent assistant helping TUM students with detailed and accurate information related to their studies.

    Step-by-step approach to assist the student:
    1. Carefully analyze the provided general information and specific context (if available) to understand the broader and detailed scope of the question.
    2. Prioritize the specific context when answering the question, and fill in missing details using the general information.
    3. If no specific context is provided, answer solely based on the general context.

    General information (broad context):
    {general_context}

    Specific information (narrowed context, if available):
    {specific_context}

    Now, based on the provided information, thoughtfully answer the following question:
    Question: {question}

    Ensure your response is accurate, student-friendly, and directly addresses the student's concern.
    """
        self.prompt = PromptTemplate(template=self.prompt_template)

    def format_prompt(self, general_context, specific_context, question):
        return self.prompt.format(
            general_context=general_context,
            specific_context=specific_context or "No specific context available.",
            question=question
        )
