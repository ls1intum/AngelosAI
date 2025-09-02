import numpy as np
import logging
import cohere
from app.models.base_model import BaseModelClient
from typing import List, Dict
import requests

class DocumentWithEmbedding:
    def __init__(self, embedding: List[float], content: str):
        """
        A class to represent a document with its corresponding embedding and content.
        
        Args:
            embedding (List[float]): The embedding vector of the document.
            content (str): The content of the document.
        """
        self.embedding = embedding
        self.content = content


class Reranker:
    def __init__(self, model: BaseModelClient, api_key_en: str, api_key_multi: str):
        """
        Initialize the Reranker with an embedding model.

        Args:
            model: The embedding model that provides an `embed()` method.
        """
        self.model = model
        # self.api_key = api_key
        self.api_key_en = api_key_en
        self.api_key_multi = api_key_multi
        self.rerank_url_en = "https://rerank-35.swedencentral.models.ai.azure.com/v1/rerank"
        self.rerank_url_multi = "https://rerank-35.swedencentral.models.ai.azure.com/v1/rerank"
        # self.rerank_model = "rerank-multilingual-v3.0"
        # self.rerank_modelEn = "rerank-english-v3.0"

    def rerank_with_cohere(self, context_list: List[str], query: str, language: str, top_n: int = 5) -> List[Dict]:
        """
        Re-ranks the context list using the Cohere reranking model deployed on Azure.

        Args:
            context_list (List[str]): List of document texts to be re-ranked.
            query (str): The query string to rerank the documents against.
            language (str): The language of the documents ('english' or other).
            top_n (int): The number of top results to return after re-ranking.

        Returns:
            List[Dict]: A list of the re-ranked document contents based on relevance.
        """
        try:
            if not context_list:
                return []
            
            # Determine the correct endpoint URL and API key based on language
            if language.lower() == "english":
                rerank_url = self.rerank_url_en
                api_key = self.api_key_en
            else:
                rerank_url = self.rerank_url_multi
                api_key = self.api_key_multi
                
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'query': query,
                'documents': context_list,
                'top_n': top_n,
                'return_documents': False
            }

            response = requests.post(rerank_url, headers=headers, json=payload)
            if response.status_code != 200:
                logging.error(f"Error during Cohere re-ranking: {response.status_code} {response.text}")
                return [{'index': i, 'relevance_score': 1.0} for i in range(min(top_n, len(context_list)))]

            results = response.json().get('results', [])
            return results

        except Exception as e:
            logging.error(f"Error during Cohere re-ranking: {e}")
            return [{'index': i, 'relevance_score': 1.0} for i in range(min(top_n, len(context_list)))]