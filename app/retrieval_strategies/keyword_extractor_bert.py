from keybert import KeyBERT

class KeywordExtractorBERT:
    """A class to extract keywords using KeyBERT for more semantically relevant keywords."""

    def __init__(self):
        # Initialize the KeyBERT model (this uses a pre-trained BERT model)
        self.model = KeyBERT()
        
    def extract_keywords(self, text: str):
        """
        Extract the most relevant keywords using KeyBERT.
        
        Args:
            text (str): The input text from which to extract keywords.
        
        Returns:
            List[str]: A list of extracted keywords (phrases).
        """
        keywords = self.model.extract_keywords(text, keyphrase_ngram_range=(2, 4), stop_words='english', top_n=6)
        return keywords
