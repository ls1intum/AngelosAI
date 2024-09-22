class PromptManager:
    def __init__(self):
        self.answer_prompt_template = """
    You are an intelligent assistant helping TUM students with detailed and accurate information related to their studies.

    Step-by-step approach to assist the student:
    1. Read the question again
    2. Carefully analyze the provided general information and study program specific context (if available). Keep in mind that not all of the provided context is relevant to the question.
    3. Prioritize the narrowed study program specific context over the general information when answering the question.
    4. If no specific context is provided, answer solely based on the general context.

    General information (broad context):
    {general_context}

    Study program specific information (narrowed context, if available):
    {specific_context}

    Now, only based on the provided information, thoughtfully answer the following question:
    Question: {question}

    Ensure your response is accurate, student-friendly, and directly addresses the student's concern.
    If you don't think you can answer this question with the provided context, simply reply with:
    'I'm sorry for the inconvenience! But I cannot answer this question with the provided context.'
    """
    
        # Adding keyword extraction template
        self.keyword_extraction_prompt_template = """
    You are a smart assistant extracting keywords for a RAG system that answers questions of students to study administration. 
    The keywords are important for ranking the retrieved context. Extract the most relevant academic and administrative keywords 
    from the student’s query. The keywords should be related to university. Give me 7 keywords between ngram 2 and ngram 4 of the following question:
    {question}
    Only respond with the keywords, separated by a comma. Do not respond with anything else.
    """

    def create_messages(self, general_context, specific_context, question):
        """Converts the template into a message format suitable for LLMs like OpenAI's GPT."""
        
        # Construct the system prompt
        system_content = self.answer_prompt_template.format(
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
    
    # Method for creating keyword extraction message
    def create_keyword_extraction_message(self, question):
        """Generates the prompt specifically for keyword extraction."""
        
        # Construct the keyword extraction prompt
        keyword_content = self.keyword_extraction_prompt_template.format(question=question)
        
        # Return the messages structure for the LLM
        return [
            {"role": "system",
             "content": "You are an intelligent assistant that helps extract relevant university-related keywords for RAG systems."},
            {"role": "user", "content": keyword_content}
        ]
