import logging
from enum import Enum

import weaviate
import weaviate.classes as wvc
from weaviate.collections import Collection
from weaviate.collections.classes.config import DataType, Configure, Property
from weaviate.collections.classes.config_vectorizers import VectorDistances
from weaviate.collections.classes.filters import Filter

from app.utils.environment import config


class DocumentSchema(Enum):
    """
    Schema for the lecture slides
    """

    COLLECTION_NAME = "DocumentSnowflake"
    STUDY_PROGRAM = "study_program"
    CONTENT = "content"
    EMBEDDING = "embedding"


class WeaviateManager:
    def __init__(self, url: str, model):
        logging.info("Initializing Weaviate Manager")
        self.client = weaviate.connect_to_local(host=config.WEAVIATE_URL, port=config.WEAVIATE_PORT)
        self.model = model
        self.schema_initialized = False
        self.documents = self._initialize_schema()

    def __del__(self):
        self.client.close()

    def _initialize_schema(self) -> Collection:
        """Creates the schema in Weaviate for storing documents and embeddings."""

        if self.client.collections.exists(DocumentSchema.COLLECTION_NAME.value):
            logging.info("existing schema ")
            return self.client.collections.get(DocumentSchema.COLLECTION_NAME.value)

        logging.info("Creating new schema")
        return self.client.collections.create(
            name=DocumentSchema.COLLECTION_NAME.value,
            # vectorizer_config=[
            #     Configure.NamedVectors.text2vec_ollama(
            #         name="embedding",  # The field in which embedding will be stored
            #         source_properties=[DocumentSchema.CONTENT.value],
            #         api_endpoint=config.OLLAMA_URL,
            #         model="snowflake-arctic-embed:latest",
            #         headers=create_auth_header()
            #     )
            # ],
            vectorizer_config=None,
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE
            ),
            properties=[
                Property(
                    name=DocumentSchema.STUDY_PROGRAM.value,
                    description="The study program of the document",
                    data_type=DataType.TEXT,
                ),
                Property(
                    name=DocumentSchema.CONTENT.value,
                    description="The content of the document",
                    data_type=DataType.TEXT,
                    index_inverted=False
                )
            ],
        )

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

    def delete_collection(self, collection_name):
        """
        Delete a collection from the database
        """
        if self.client.collections.exists(collection_name):
            if self.client.collections.delete(collection_name):
                logging.info(f"Collection {collection_name} deleted")
            else:
                logging.error(f"Collection {collection_name} failed to delete")

    def add_documents(self, chunks, study_program: str):
        # docs = list()
        # for i, chunk in enumerate(chunks):
        #     text_embedding = self.model.embed(chunk.page_content)
        #     docs.append(wvc.data.DataObject(
        #         properties={DocumentSchema.CONTENT.value: chunk.page_content,
        #                     DocumentSchema.STUDY_PROGRAM.value: study_program},
        #         vector=text_embedding
        #     ))
        # collection = self.client.collections.get(DocumentSchema.COLLECTION_NAME.value)
        # collection.data.insert_many(chunks)

        with self.documents.batch.rate_limit(requests_per_minute=600) as batch:
            try:
                for index, chunk in enumerate(chunks):
                    embed_chunk = self.model.embed(
                        chunk.page_content
                    )
                    batch.add_object(properties={DocumentSchema.CONTENT.value: chunk.page_content,
                                                 DocumentSchema.STUDY_PROGRAM.value: study_program},
                                     vector=embed_chunk)
            except Exception as e:
                logging.error(f"Error updating lecture unit: {e}")
