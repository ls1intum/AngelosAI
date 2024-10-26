import os
from testing.models.azure_testing_model import AzureTestingModel
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables from .env file
load_dotenv()

class EmbeddingEvaluation:
    def __init__(self, model: AzureTestingModel):
        """
        Initialize the EmbeddingEvaluation class, setting up OpenAI API key and model configuration.
        """
        self.model = model

    def get_embedding(self, text):
        """
        Get the embedding for the input text using the OpenAI API.
        """
        try:
            return self.model.embed(text)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def cosine_similarity(self, embedding1: list[float], embedding2: list[float]):
        """
        Calculate the cosine similarity between two embeddings.
        """
        # Convert the embeddings to 2D numpy arrays for use in cosine_similarity
        embedding1 = np.array(embedding1).reshape(1, -1)
        embedding2 = np.array(embedding2).reshape(1, -1)
        return cosine_similarity(embedding1, embedding2)[0][0]

    def euclidean_distance(self, embedding1, embedding2):
        """
        Calculate the Euclidean distance between two embeddings.
        """
        # Convert embeddings to numpy arrays and calculate Euclidean distance
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        return np.linalg.norm(embedding1 - embedding2)

    def evaluate_similarity(self, gt_answer, answer):
        """
        Evaluate the similarity between the ground truth answer (gt_answer) and the provided answer using embeddings.
        Returns both cosine similarity and Euclidean distance.
        """

        # Get embeddings for both answers
        gt_embedding = self.get_embedding(gt_answer)
        answer_embedding = self.get_embedding(answer)

        # If either embedding fails, return None
        if gt_embedding is None or answer_embedding is None:
            return {
                'cosine_similarity': None,
                'euclidean_distance': None
            }

        # Calculate similarity scores
        cosine_sim = self.cosine_similarity(gt_embedding, answer_embedding)
        euclidean_dist = self.euclidean_distance(gt_embedding, answer_embedding)

        # Return the similarity scores
        return {
            'cosine_similarity': cosine_sim,
            'euclidean_distance': euclidean_dist
        }
