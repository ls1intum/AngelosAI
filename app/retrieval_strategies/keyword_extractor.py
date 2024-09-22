import spacy
import logging
from keyword_spacy import KeywordExtractor as SpacyKeywordExtractor

class KeywordExtractor:
    """A class to extract keywords from text using spaCy's keyword extraction pipeline."""

    # Load the spaCy model and add the keyword extractor pipe
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe("keyword_extractor", last=True, config={"top_n": 8, "min_ngram": 2, "max_ngram": 3, "strict": False})

    @staticmethod
    def extract_keywords(text: str):
        """
        Extract the top keywords from a given text using spaCy and keyword-spacy.
        
        Args:
            text (str): The input text from which to extract keywords.
        
        Returns:
            List[str]: A list of extracted keywords (n-grams).
        """
        doc = KeywordExtractor.nlp(text)
        
        return doc._.keywords
    