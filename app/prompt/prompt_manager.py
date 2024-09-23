class PromptManager:
    def __init__(self):
        self.answer_prompt_template = """
    You are an intelligent assistant helping TUM students with detailed and accurate information related to their studies.

    **Instructions:**
    - Re-read the question carefully.
    - Analyze the provided general information and, if available, study program-specific context.
    - Prioritize study program-specific context over general information.
    - If no specific context is provided, base your answer solely on the general context.

    **General Information:**
    {general_context}

    **Study Program Specific Information:**
    {specific_context}

    **Question:**
    {question}

    **Response:**
    - Be clear and concise.
    - Use a friendly and professional tone.
    - Avoid unnecessary jargon.
    - Keep the response within 200 words.

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
             "content": "You are an intelligent assistant that helps students of the Technical University of Munich (TUM) with questions related to their studies."},
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
