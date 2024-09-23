import logging
from enum import Enum
from typing import List

import weaviate
import weaviate.classes as wvc
from langchain.docstore.document import Document
from weaviate.collections import Collection
from weaviate.collections.classes.config import DataType, Configure, Property
from weaviate.collections.classes.config_vectorizers import VectorDistances
from weaviate.collections.classes.filters import Filter

from app.models.base_model import BaseModelClient
from app.models.openai_model import OpenAIModel
from app.utils.environment import config


class DocumentSchema(Enum):
    """
    Schema for the embedded chunks
    """

    COLLECTION_NAME = "DocumentMxbai"
    STUDY_PROGRAM = "study_program"
    CONTENT = "content"
    EMBEDDING = "embedding"


class WeaviateManager:
    def __init__(self, url: str, embedding_model: BaseModelClient):
        logging.info("Initializing Weaviate Manager")
        self.client = weaviate.connect_to_local(host=config.WEAVIATE_URL, port=config.WEAVIATE_PORT)
        self.model = embedding_model
        self.schema_initialized = False
        self.documents = self.initialize_schema()

    def __del__(self):
        self.client.close()

    def initialize_schema(self) -> Collection:
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

        try:
            # Create the collection with the specified configuration
            collection = self.client.collections.create(
                name=collection_name,
                description="A collection for storing study-related documents for RAG system",
                properties=properties,
                vector_index_config=vector_index_config,
                vectorizer_config=None  # Since we are manually providing embeddings
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
        try:
            text_embedding = self.model.embed(text)
            # logging.info(f"Adding document with embedding: {text_embedding}")
            self.documents.data.insert(properties={DocumentSchema.CONTENT.value: text,
                                                   DocumentSchema.STUDY_PROGRAM.value: study_program},
                                       vector=text_embedding)
            logging.info(f"Document successfully added with study program: {study_program}")
        except Exception as e:
            logging.error(f"Failed to add document: {e}")

    def get_relevant_context(self, question: str, study_program: str):
        """Retrieve documents based on the question embedding and study program."""
        try:
            question_embedding = self.model.embed(question)  # Embed the query
            query_result = self.documents.query.near_vector(
                near_vector=question_embedding,
                filters=Filter.by_property(DocumentSchema.STUDY_PROGRAM.value).equal(study_program),
                limit=5,
                return_metadata=wvc.query.MetadataQuery(certainty=True)
            )
            for result in query_result.objects:
                print(result.properties)
                print(result.metadata)

            context = "\n\n".join(result.properties['content'] for result in query_result.objects)
            logging.info(context)
            return context
        except Exception as e:
            logging.error(f"Error retrieving relevant context: {e}")
            return ""

    def get_relevant_context_as_list(self, question: str, study_program: str):
        """Retrieve documents based on the question embedding and study program and context as list for test mode."""
        try:
            question_embedding = self.model.embed(question)  # Embed the query
            query_result = self.documents.query.near_vector(
                near_vector=question_embedding,
                filters=Filter.by_property(DocumentSchema.STUDY_PROGRAM.value).equal(study_program),
                limit=5,
                return_metadata=wvc.query.MetadataQuery(certainty=True)
            )
            for result in query_result.objects:
                print(result.properties)
                print(result.metadata)

            context = "\n\n".join(result.properties['content'] for result in query_result.objects)
            context_list = [result.properties['content'] for result in query_result.objects]
            logging.info(context)
            logging.info(context_list)
            return context, context_list
        except Exception as e:
            logging.error(f"Error retrieving relevant context: {e}")
            return ""

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
