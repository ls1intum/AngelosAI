import numpy as np
import logging
import cohere
from app.models.base_model import BaseModelClient
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

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
    def __init__(self, model: BaseModelClient, api_key: str):
        """
        Initialize the Reranker with an embedding model.

        Args:
            model: The embedding model that provides an `embed()` method.
        """
        self.model = model
        self.api_key = api_key
        self.rerank_model = "rerank-multilingual-v3.0"

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

    def rerank_with_cohere(self, context_list: List[str], query: str, top_n: int = 5) -> List[str]:
        """
        Re-ranks the context list using the Cohere reranking model and logs the document indexes based on relevance.

        Args:
            context_list (List[str]): List of document texts to be re-ranked.
            query (str): The query string to rerank the documents against.
            top_n (int): The number of top results to return after re-ranking (default is 3).

        Returns:
            List[str]: A list of the re-ranked document contents based on relevance.
        """
        try:
            # Initialize Cohere client with the API key
            co = cohere.Client(self.api_key)

            # Use Cohere's reranking model to rank the documents based on the query
            response = co.rerank(
                model=self.rerank_model,
                query=query,
                documents=context_list,
                top_n=top_n
            )

            # Log the relevance scores and indexes of the reranked documents
            for result in response.results:
                logging.info(f"Document index: {result.index}, Relevance score: {result.relevance_score}")

            # Get the ranked documents based on the response indexes
            ranked_context_list = [context_list[result.index] for result in response.results]

            return ranked_context_list[:top_n]
        except Exception as e:
            logging.error(f"Error during Cohere re-ranking: {e}")
            return context_list