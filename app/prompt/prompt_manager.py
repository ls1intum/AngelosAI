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
    If you don't think you can answer this question with the provided context, give a standard answer like:
    'I'm sorry for the inconvenience! But I cannot answer this question with the provided context.'
    """

    def create_messages(self, general_context, specific_context, question):
        """Converts the template into a message format suitable for LLMs like OpenAI's GPT."""

        # Construct the system prompt
        system_content = self.prompt_template.format(
            general_context=general_context,
            specific_context=specific_context or "No specific context available.",
            question=question
        )

        # Return the messages structure for the LLM
        return [
            {"role": "system",
             "content": "You are an intelligent assistant that helps TUM students with their studies."},
            {"role": "user", "content": system_content}
        ]
