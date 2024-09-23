import logging
from enum import Enum
from typing import List, Union, Tuple
from app.models.openai_model import OpenAIModel
from app.models.base_model import BaseModelClient
from app.retrieval_strategies.keyword_extractor_bert import KeywordExtractorBERT
from langchain.docstore.document import Document
from app.retrieval_strategies.reranker import Reranker, DocumentWithEmbedding

import weaviate
import weaviate.classes as wvc
from weaviate.collections import Collection
from weaviate.collections.classes.config import DataType, Configure, Property
from weaviate.classes.query import Rerank
from weaviate.collections.classes.config_vectorizers import VectorDistances
from weaviate.collections.classes.filters import Filter

from app.utils.environment import config


class DocumentSchema(Enum):
    """
    Schema for the embedded chunks
    """

    COLLECTION_NAME = "CITKnowledgeBase"
    STUDY_PROGRAM = "study_program"
    CONTENT = "content"
    EMBEDDING = "embedding"


class WeaviateManager:
    def __init__(self, url: str, embedding_model: BaseModelClient, reranker: Reranker):
        logging.info("Initializing Weaviate Manager")
        self.client = weaviate.connect_to_local(host=config.WEAVIATE_URL, port=config.WEAVIATE_PORT)
        self.model = embedding_model
        self.schema_initialized = False
        self.documents = self._initialize_schema()
        self.reranker = reranker

    def __del__(self):
        self.client.close()

    def _initialize_schema(self) -> Collection:
        """Creates the schema in Weaviate for storing documents and embeddings."""

        collection_name = DocumentSchema.COLLECTION_NAME.value

        # Check if the collection already exists
        if self.client.collections.exists(collection_name):
            logging.info(f"Existing schema found for {collection_name}")
            return self.client.collections.get(collection_name)

        logging.info(f"Creating new schema for {collection_name}")
        # Define properties for the collection
        properties = [
            Property(
                name=DocumentSchema.STUDY_PROGRAM.value,
                description="The study program of the document",
                data_type=DataType.TEXT,
                index_filterable=True,
                index_range_filters=True,
                index_searchable=True
            ),
            Property(
                name=DocumentSchema.CONTENT.value,
                description="The content of the document",
                data_type=DataType.TEXT,
                index_inverted=False  # Disable inverted index if not needed
            )
        ]

        # Define vector index configuration (use cosine distance metric)
        vector_index_config = Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE
        )

        # Defne inverted index configuration
        inverted_index_config = Configure.inverted_index(
            index_property_length= True
        )

        try:
            # Create the collection with the specified configuration
            collection = self.client.collections.create(
                name=collection_name,
                description="A collection for storing study-related documents for RAG system",
                properties=properties,
                vector_index_config=vector_index_config,
                vectorizer_config=None,  # Since we are manually providing embeddings
                inverted_index_config=inverted_index_config,
            )
            logging.info(f"Schema for {collection_name} created successfully")
            self.schema_initialized = True
            return collection
        except weaviate.WeaviateInvalidInputError as e:
            logging.error(f"Invalid input error while creating schema: {e}")
        except weaviate.WeaviateConnectionError as e:
            logging.error(f"Connection error while creating schema: {e}")
        except weaviate.UnexpectedStatusCodeError as e:
            logging.error(f"Unexpected status code while creating schema: {e}")
        except Exception as e:
            logging.error(f"Error creating schema for {collection_name}: {e}")

    def add_document(self, text: str, study_program: str):
        """Add a document with classification to Weaviate."""
        text_embedding = self.model.embed(text)
        # logging.info(f"Adding document with embedding: {text_embedding}")
        self.documents.data.insert(properties={DocumentSchema.CONTENT.value: text,
                                                DocumentSchema.STUDY_PROGRAM.value: study_program},
                                    vector=text_embedding)
        logging.info(f"Document successfully added with study program: {study_program}")

    def get_relevant_context(self, question: str, study_program: str, keywords: str = None, test_mode: bool = False) -> Union[str, Tuple[str, List[str]]]:
        """
        Retrieve relevant documents based on the question embedding and study program.
        Optionally returns both the concatenated context and the sorted context list for testing purposes.

        Args:
            question (str): The student's question.
            study_program (str): The study program of the student.
            keywords (str, optional): Extracted keywords for boosting. Defaults to None.
            test_mode (bool, optional): If True, returns both context and sorted_context. Defaults to False.

        Returns:
            Union[str, Tuple[str, List[str]]]: 
                - If test_mode is False: Returns the concatenated context string.
                - If test_mode is True: Returns a tuple of (context, sorted_context list).
        """
        try:
            # Define the number of documents to retrieve
            limit = 10
            if study_program.lower() != "general":
                limit = 10  # Adjust this value if needed based on study program specificity

            # Embed the question using the embedding model
            question_embedding = self.model.embed(question)

            # Normalize the study program name and calculate its length
            study_program = WeaviateManager.normalize_study_program_name(study_program)
            study_program_length = len(study_program)

            # logging.info(f"Keywords: {keywords}")

            # Perform the vector-based query with filters
            query_result = self.documents.query.near_vector(
                near_vector=question_embedding,
                filters=Filter.all_of([
                    Filter.by_property(DocumentSchema.STUDY_PROGRAM.value).equal(study_program),
                    Filter.by_property(DocumentSchema.STUDY_PROGRAM.value, length=True).equal(study_program_length),
                ]),
                limit=limit,
                # include_vector=True,
                return_metadata=wvc.query.MetadataQuery(certainty=True, score=True, distance=True)
            )
            # documents_with_embeddings: List[DocumentWithEmbedding] = []
            for result in query_result.objects:
                logging.info(f"Certainty: {result.metadata.certainty}, Score: {result.metadata.score}, Distance: {result.metadata.distance}")
                # documents_with_embeddings.append(DocumentWithEmbedding(content=result.properties['content'], embedding=result.vector['default']))
            
            # sorted_context = self.reranker.rerank_with_embeddings(documents_with_embeddings, keyword_string=keywords)

            context_list = [result.properties['content'] for result in query_result.objects]

            # Remove exact duplicates from context_list
            context_list = WeaviateManager.remove_exact_duplicates(context_list)
            logging.info(f"Context list length after removing exact duplicates: {len(context_list)}")

            # Rerank the unique contexts using Cohere
            sorted_context = self.reranker.rerank_with_cohere(context_list=context_list, query=question, top_n=5)
            context = "\n\n".join(sorted_context)

            # Return based on test_mode
            if test_mode:
                return context, sorted_context
            else:
                return context

        except Exception as e:
            logging.error(f"Error retrieving relevant context: {e}")
            return "" if not test_mode else ("", [])

    def delete_collection(self):
        """
        Delete a collection from the database
        """
        collection_name = DocumentSchema.COLLECTION_NAME.value

        if self.client.collections.exists(collection_name):
            try:
                self.client.collections.delete(collection_name)
                logging.info(f"Collection {collection_name} deleted")
                return True
            except Exception as e:
                logging.error(f"Failed to delete collection {collection_name}: {str(e)}")
                return False
        else:
            logging.warning(f"Collection {collection_name} does not exist")
            return False
        

    def add_documents(self, chunks: List[Document], study_program: str):
        try:
            # Make use of OpenAI mass batch embedding
            if isinstance(self.model, OpenAIModel):
                texts = [chunk.page_content for chunk in chunks]
                embeddings = self.model.embed_batch(texts)
            else:
                # For other models, embed each chunk one at a time
                embeddings = [self.model.embed(chunk.page_content) for chunk in chunks]

            # Add the chunks to the vector database in a batch
            with self.documents.batch.rate_limit(requests_per_minute=600) as batch:
                for index, chunk in enumerate(chunks):
                    batch.add_object(properties={
                        DocumentSchema.CONTENT.value: chunk.page_content,
                        DocumentSchema.STUDY_PROGRAM.value: study_program
                    }, vector=embeddings[index])

        except Exception as e:
            logging.error(f"Error adding document {e}")

    @staticmethod
    def normalize_study_program_name(study_program: str) -> str:
        """Normalize study program names to a consistent format."""
        # Lowercase and replace spaces with hyphens
        return study_program.strip().lower().replace(" ", "-")
    
    @staticmethod
    def remove_exact_duplicates(context_list: List[str]) -> List[str]:
        seen = set()
        unique_context = []
        for context in context_list:
            if context not in seen:
                unique_context.append(context)
                seen.add(context)
        return unique_context
