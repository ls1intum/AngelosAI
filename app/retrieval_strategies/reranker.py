import numpy as np
import logging
import cohere
from app.models.base_model import BaseModelClient
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
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
        self.rerank_url_en = "https://rerankv3-en.swedencentral.models.ai.azure.com/v1/rerank"
        self.rerank_url_multi = "https://rerankv3-multi.swedencentral.models.ai.azure.com/v1/rerank"
        # self.rerank_model = "rerank-multilingual-v3.0"
        # self.rerank_modelEn = "rerank-english-v3.0"

    def rerank_with_embeddings(self, context_list: List[DocumentWithEmbedding], keyword_string: str) -> List[str]:
        """
        Re-rank the context list based on cosine similarity between keyword embeddings and document embeddings.

        Args:
            context_list (List[DocumentWithEmbedding]): List of DocumentWithEmbedding objects to be re-ranked.
            keyword_string (str): Keyword string or query to compare against the context.

        Returns:
            ranked_context_list (List[str]): Context (content) list re-ranked based on similarity.
        """
        # Generate embedding for the keyword string
        keyword_embedding = self.model.embed(keyword_string)

        # Calculate cosine similarity between the keyword embedding and each document embedding
        cosine_similarities = [
            cosine_similarity([keyword_embedding], [doc_embedding.embedding]).flatten()[0] 
            for doc_embedding in context_list
        ]

        # Rank the documents based on cosine similarity (in descending order)
        ranked_indices = np.argsort(-np.array(cosine_similarities))

        logging.info(f"Ranked indices: {ranked_indices}")

        # Extract the content from the ranked DocumentWithEmbedding objects
        ranked_context_list = [context_list[i].content for i in ranked_indices]

        return ranked_context_list

    def rerank_with_cohere(self, context_list: List[str], query: str, language: str, min_relevance_score: float, top_n: int = 5) -> List[str]:
        """
        Re-ranks the context list using the Cohere reranking model deployed on Azure.

        Args:
            context_list (List[str]): List of document texts to be re-ranked.
            query (str): The query string to rerank the documents against.
            language (str): The language of the documents ('english' or other).
            min_relevance_score (float): The minimum relevance score to consider.
            top_n (int): The number of top results to return after re-ranking.

        Returns:
            List[str]: A list of the re-ranked document contents based on relevance.
        """
        try:
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
                return context_list[:top_n]

            response_json = response.json()

            # Log the full response from the API for debugging
            logging.info(f"Cohere full response: {response_json}")
            results = response_json.get('results', [])

            # Log the ranked documents that are in the top_n
            ranked_indices = []
            for i, result in enumerate(results):
                index = result['index']
                relevance_score = result.get('relevance_score')
                # Filter results based on min_relevance_score
                if relevance_score >= min_relevance_score:
                    ranked_indices.append(index)

            # Get the ranked documents based on the indices
            ranked_context_list = [context_list[result['index']] for result in results]

            return ranked_context_list

        except Exception as e:
            logging.error(f"Error during Cohere re-ranking: {e}")
            return context_list[:top_n]