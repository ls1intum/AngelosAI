import logging
from enum import Enum
from typing import List, Union, Tuple, Optional, Dict

import weaviate
import weaviate.classes as wvc
from weaviate.collections import Collection
from weaviate.collections.classes.config import DataType, Configure, Property, Tokenization
from weaviate.collections.classes.config_vectorizers import VectorDistances
from weaviate.collections.classes.filters import Filter

from app.data.database_requests import DatabaseDocument, DatabaseSampleQuestion, DatabaseDocumentMetadata, \
    SampleQuestion
from app.models.base_model import BaseModelClient
from app.models.ollama_model import OllamaModel
from app.post_retrieval.reranker import Reranker
from app.utils.environment import config


class DocumentSchema(Enum):
    """
    Schema for the embedded chunks
    """
    COLLECTION_NAME = "CITKnowledgeBase"
    KNOWLEDGE_BASE_ID = "kb_id"
    STUDY_PROGRAMS = "study_programs"
    CONTENT = "content"
    LINK = "link"
    ORGANISATION_ID = "org_id"


class QASchema(Enum):
    """
    Schema for the QA Collection
    """
    COLLECTION_NAME = "QACollection"
    KNOWLEDGE_BASE_ID = "kb_id"
    TOPIC = "topic"
    STUDY_PROGRAMS = "study_programs"
    QUESTION = "question"
    ANSWER = "answer"
    ORGANISATION_ID = "org_id"


class WeaviateManager:
    def __init__(self, url: str, embedding_model: BaseModelClient, reranker: Reranker):
        logging.info("Initializing Weaviate Manager")
        self.client = weaviate.connect_to_local(host=config.WEAVIATE_URL, port=config.WEAVIATE_PORT)
        self.model = embedding_model
        self.schema_initialized = False
        self.reranker = reranker

        if config.DELETE_BEFORE_INIT.lower() == "true":
            logging.warning("Deleting existing data before initialization...")
            self.delete_collections()

        self.documents = self.initialize_schema()
        self.qa_collection = self.initialize_qa_schema()

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
                name=DocumentSchema.KNOWLEDGE_BASE_ID.value,
                description="The Angelos ID of the document",
                data_type=DataType.TEXT,
                index_filterable=True,
                index_range_filters=False,
                index_searchable=False
            ),
            Property(
                name=DocumentSchema.STUDY_PROGRAMS.value,
                description="The study program of the document",
                data_type=DataType.TEXT_ARRAY,
                index_filterable=True,
                index_range_filters=False,
                index_searchable=False,
                index_inverted=True,
                tokenization=Tokenization.FIELD
            ),
            Property(
                name=DocumentSchema.CONTENT.value,
                description="The content of the document",
                data_type=DataType.TEXT,
                index_inverted=False
            ),
            Property(
                name=DocumentSchema.LINK.value,
                description="The link of the document",
                data_type=DataType.TEXT,
                index_inverted=False
            ),
            Property(
                name=DocumentSchema.ORGANISATION_ID.value,
                description="The Organisation ID of the document",
                data_type=DataType.INT,
                index_filterable=True,
                index_range_filters=False,
                index_searchable=False
            ),
        ]

        # Define vector index configuration (use cosine distance metric)
        vector_index_config = Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE
        )

        # Defne inverted index configuration
        inverted_index_config = Configure.inverted_index(
            index_property_length=True
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
        except weaviate.exceptions.WeaviateInvalidInputError as e:
            logging.error(f"Invalid input error while creating schema: {e}")
        except weaviate.exceptions.WeaviateConnectionError as e:
            logging.error(f"Connection error while creating schema: {e}")
        except weaviate.exceptions.UnexpectedStatusCodeError as e:
            logging.error(f"Unexpected status code while creating schema: {e}")
        except Exception as e:
            logging.error(f"Error creating schema for {collection_name}: {e}")

    def initialize_qa_schema(self) -> Collection:
        """Creates the schema in Weaviate for storing questions and answers."""

        collection_name = QASchema.COLLECTION_NAME.value

        # Check if the collection already exists
        if self.client.collections.exists(collection_name):
            logging.info(f"Existing schema found for {collection_name}")
            return self.client.collections.get(collection_name)

        logging.info(f"Creating new schema for {collection_name}")

        # Define properties for the QA collection
        properties = [
            Property(
                name=QASchema.KNOWLEDGE_BASE_ID.value,
                description="The Angelos ID of the sample question",
                data_type=DataType.TEXT,
                index_filterable=True,
                index_range_filters=False,
                index_searchable=False
            ),
            Property(
                name=QASchema.TOPIC.value,
                description="The topic of the sample question",
                data_type=DataType.TEXT,
                index_inverted=False
            ),
            Property(
                name=QASchema.STUDY_PROGRAMS.value,
                description="The relevant study program",
                data_type=DataType.TEXT_ARRAY,
                index_filterable=True,
                index_range_filters=False,
                index_searchable=False,
                index_inverted=True,
                tokenization=Tokenization.FIELD
            ),
            Property(
                name=QASchema.QUESTION.value,
                description="The student's question",
                data_type=DataType.TEXT,
                index_inverted=False
            ),
            Property(
                name=QASchema.ANSWER.value,
                description="The academic advisor's answer",
                data_type=DataType.TEXT,
                index_inverted=False
            ),
            Property(
                name=QASchema.ORGANISATION_ID.value,
                description="The Organisation ID of the sample question",
                data_type=DataType.INT,
                index_filterable=True,
                index_range_filters=False,
                index_searchable=False
            ),
        ]

        # Define vector index configuration
        vector_index_config = Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE
        )

        inverted_index_config = Configure.inverted_index(
            index_property_length=True
        )

        try:
            # Create the QA collection with the specified configuration
            collection = self.client.collections.create(
                name=collection_name,
                description="A collection for storing sample questions and answers for the RAG system",
                properties=properties,
                vector_index_config=vector_index_config,
                vectorizer_config=None,  # Since we are manually providing embeddings
                inverted_index_config=inverted_index_config,
            )
            logging.info(f"Schema for {collection_name} created successfully")
            return collection
        except weaviate.exceptions.WeaviateInvalidInputError as e:
            logging.error(f"Invalid input error while creating schema: {e}")
        except weaviate.exceptions.WeaviateConnectionError as e:
            logging.error(f"Connection error while creating schema: {e}")
        except weaviate.exceptions.UnexpectedStatusCodeError as e:
            logging.error(f"Unexpected status code while creating schema: {e}")
        except Exception as e:
            logging.error(f"Error creating schema for {collection_name}: {e}")
            
    def get_question_embedding(self, question: str) -> List[float]:
        question_embedding = self.model.embed(question)
        return question_embedding


    def get_relevant_context(self, question_embedding: List[float], study_program: str, org_id: Optional[int],
                             limit=10, filter_by_org: bool = True) -> List[Dict]:
        """
        Retrieves relevant context documents based on the given question embedding and study program.

        Args:
            question_embedding (List[float]): The vector embedding representing the student's question.
            study_program (str): The name of the study program to filter documents.
            org_id (Optional[int]): The organization ID to filter documents (if applicable).
            limit (int, optional): The maximum number of documents to retrieve. Defaults to 10.
            filter_by_org (bool, optional): Whether to filter results by organization ID. Defaults to True.

        Returns:
            List[Dict]: A list of document dictionaries relevant to the query.
        """
        try:
            # Normalize the study program name
            study_program = WeaviateManager.normalize_study_program_name(study_program)

            # Define filter
            if filter_by_org and org_id is not None:
                filters = Filter.all_of([
                    Filter.by_property(DocumentSchema.STUDY_PROGRAMS.value).contains_any([study_program]),
                    Filter.by_property(DocumentSchema.ORGANISATION_ID.value).equal(org_id),
                ])
            else:
                filters = Filter.by_property(DocumentSchema.STUDY_PROGRAMS.value).contains_any([study_program])


            # Perform the vector-based query with filters
            query_result = self.documents.query.near_vector(
                near_vector=question_embedding,
                filters=filters,
                limit=limit,
                # include_vector=True,
                return_metadata=wvc.query.MetadataQuery(certainty=True, score=True, distance=True)
            )

            context_list = [
                {
                    'content': result.properties[DocumentSchema.CONTENT.value],
                    'link': result.properties.get(DocumentSchema.LINK.value, None)
                }
                for result in query_result.objects
            ]
            
            return context_list

        except Exception as e:
            logging.error(f"Error retrieving relevant context: {e}")
            # tb = traceback.format_exc()
            # logging.error("Traceback:\n%s", tb)
            return []


    def get_relevant_sample_questions(self, question: str, question_embedding: List[float], language: str, org_id: int) -> List[SampleQuestion]:
        """
        Retrieves relevant sample questions and their answers based on the provided question and its embedding.

        Args:
            question (str): The original student question.
            question_embedding (List[float]): The vector embedding of the question.
            language (str): The language of the question.
            org_id (int): The organization ID to filter sample questions.

        Returns:
            List[SampleQuestion]: A list of SampleQuestion objects, sorted by relevance.
        """
        try:
            limit = 5
            top_n = 3
            min_relevance_score = 0.5

            query_result = self.qa_collection.query.near_vector(
                near_vector=question_embedding,
                limit=limit,
                filters=Filter.by_property(DocumentSchema.ORGANISATION_ID.value).equal(org_id),
                return_metadata=wvc.query.MetadataQuery(certainty=True, score=True, distance=True)
            )

            # Collect the results
            sample_questions: List[SampleQuestion] = []
            for result in query_result.objects:
                topic = result.properties.get(QASchema.TOPIC.value, "")
                retrieved_question = result.properties.get(QASchema.QUESTION.value, "")
                answer = result.properties.get(QASchema.ANSWER.value, "")
                study_programs = result.properties.get(QASchema.STUDY_PROGRAMS, [])
                sample_questions.append(SampleQuestion(topic=topic, question=retrieved_question, answer=answer,
                                                       study_programs=study_programs))

            # Rerank the sample questions using the reranker
            context_list = [
                (f"Question: {sq.question}\nAnswer: {sq.answer}" if language == "English"
                else f"Frage: {sq.question}\nAntwort: {sq.answer}")
                for sq in sample_questions
            ]
            
            rerank_results = self.reranker.rerank_with_cohere(
                context_list=context_list, query=question, language=language, top_n=top_n,
            )

            sorted_sample_questions: List[SampleQuestion] = []
            for result in rerank_results:
                idx = result['index']
                score = result['relevance_score']
                if score >= min_relevance_score and idx < len(sample_questions):
                    sorted_sample_questions.append(sample_questions[idx])

            return sorted_sample_questions

        except Exception as e:
            logging.error(f"Error retrieving relevant sample questions: {e}")
            return []

    def delete_collections(self):
        """
        Delete a collection from the database
        """
        try:
            self.client.collections.delete_all()
            logging.info(f"Collections deleted")
            return True
        except Exception as e:
            logging.error(f"Failed to delete collections: {str(e)}")
            return False

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

    def add_documents(self, chunks: List[DatabaseDocument]):
        """
        Add chunks of DatabaseDocument objects to the vector database.
        """
        try:
            batch_size = 500
            num_chunks = len(chunks)
            logging.info(f"Adding {num_chunks} documents in batches of {batch_size}")

            # If using OpenAI model, split the chunks into batches of 500
            for i in range(0, num_chunks, batch_size):
                chunk_batch = chunks[i:i + batch_size]
                if isinstance(self.model, OllamaModel):
                    # For Ollama models, embed each chunk one at a time
                    embeddings = [self.model.embed(chunk.content) for chunk in chunk_batch]
                else:
                    texts = [chunk.content for chunk in chunk_batch]
                    embeddings = self.model.embed_batch(texts)  # Embed in batch
                logging.info(f"Chunk batch size: {len(chunk_batch)}")

                # Add the chunks to the vector database in a batch
                with self.documents.batch.rate_limit(requests_per_minute=600) as batch:
                    for index, chunk in enumerate(chunk_batch):
                        # Prepare properties
                        properties = {
                            DocumentSchema.KNOWLEDGE_BASE_ID.value: chunk.id,
                            DocumentSchema.CONTENT.value: chunk.content,
                            DocumentSchema.LINK.value: chunk.link,
                            DocumentSchema.STUDY_PROGRAMS.value: chunk.study_programs,
                            DocumentSchema.ORGANISATION_ID.value: chunk.org_id
                        }

                        # Add the document chunk to the batch
                        batch.add_object(properties=properties, vector=embeddings[index])

        except Exception as e:
            logging.error(f"Error adding document: {e}")
            raise

    def delete_by_kb_id(self, kb_id: str, return_metadata: bool) -> Optional[DatabaseDocumentMetadata]:
        """
        Delete all database entries by kb_id and return other properties
        """
        try:
            if return_metadata:
                query_result = self.documents.query.fetch_objects(
                    filters=Filter.by_property(DocumentSchema.KNOWLEDGE_BASE_ID.value).equal(kb_id)
                )

                if not query_result.objects:
                    logging.info(f"No documents found with knowledge_base_id: {kb_id}")
                    return None
                else:
                    result = query_result.objects[0]
                    properties = result.properties
                    metadata = DatabaseDocumentMetadata(
                        link=properties[DocumentSchema.LINK.value],
                        study_programs=properties[DocumentSchema.STUDY_PROGRAMS.value],
                        org_id=properties[DocumentSchema.ORGANISATION_ID.value]
                    )
                    self.documents.data.delete_many(
                        where=Filter.by_property(DocumentSchema.KNOWLEDGE_BASE_ID.value).equal(kb_id)
                    )
                    return metadata
            else:
                self.documents.data.delete_many(
                    where=Filter.by_property(DocumentSchema.KNOWLEDGE_BASE_ID.value).equal(kb_id)
                )
                return None

        except Exception as e:
            logging.error(f"Error deleting documents: {e}")

    def delete_documents(self, kb_ids: List[str]):
        """Batch delete all documents where knowledge base ID is in the provided list."""
        try:
            self.documents.data.delete_many(
                where=Filter.by_property(DocumentSchema.KNOWLEDGE_BASE_ID.value).contains_any(kb_ids)
            )
        except Exception as e:
            logging.error(f"Error deleting documents: {e}")

    def update_documents(self, kb_id: str, document: DatabaseDocumentMetadata):
        try:
            query_result = self.documents.query.fetch_objects(
                filters=Filter.by_property(DocumentSchema.KNOWLEDGE_BASE_ID.value).equal(kb_id)
            )

            if not query_result.objects:
                logging.info(f"No documents found with knowledge_base_id: {document.id}")
                return

            # Iterate through the results and update the properties
            for result in query_result.objects:
                uuid = result.uuid
                properties = result.properties
                properties[DocumentSchema.LINK.value] = document.link  # Update the link
                properties[DocumentSchema.STUDY_PROGRAMS.value] = document.study_programs  # Update the study programs

                # Reinsert the object with the updated properties
                self.documents.data.update(
                    uuid=uuid,
                    properties=properties
                )

            logging.info(f"Updated documents with knowledge_base_id: {kb_id}")
        except Exception as e:
            logging.error(f"Error updating documents with knowledge_base_id {kb_id}: {e}")
            raise

    def add_sample_question(self, sample_question: DatabaseSampleQuestion):
        """
        Adds a sample question to the QA collection in Weaviate.

        Args:
        - The SampleQuestion to add

        Returns:
        - None
        """
        try:
            # Prepare the data entry for insertion
            kb_id = sample_question.id
            topic = sample_question.topic
            study_programs = sample_question.study_programs
            question = sample_question.question
            answer = sample_question.answer
            org_id = sample_question.org_id
            
            embedding = self.model.embed(question)

            self.qa_collection.data.insert(
                properties={
                    QASchema.KNOWLEDGE_BASE_ID.value: kb_id,
                    QASchema.TOPIC.value: topic,
                    QASchema.STUDY_PROGRAMS.value: study_programs,
                    QASchema.QUESTION.value: question,
                    QASchema.ANSWER.value: answer,
                    QASchema.ORGANISATION_ID.value: org_id
                },
                vector=embedding
            )
            logging.info(f"Inserted QA pair with topic: {sample_question.topic}")
        except Exception as e:
            logging.error(f"Failed to insert sample question with topic {sample_question.topic}: {e}")
            raise

    def add_sample_questions(self, questions: List[DatabaseSampleQuestion]):
        """
        Add multiple sample questions to the QA collection in Weaviate.
        Batches the embedding and insertion process for efficiency.
        """
        try:
            batch_size = 500
            num_questions = len(questions)
            logging.info(f"Adding {num_questions} sample questions in batches of {batch_size}")

            for i in range(0, num_questions, batch_size):
                question_batch = questions[i:i + batch_size]

                if isinstance(self.model, OllamaModel):
                    # For Ollama models, embed each question one at a time
                    embeddings = [self.model.embed(q.question) for q in question_batch]
                else:
                    # For other models, embed in batch
                    texts = [q.question for q in question_batch]
                    embeddings = self.model.embed_batch(texts)

                # Insert into the QA collection in a batch
                with self.qa_collection.batch.rate_limit(requests_per_minute=600) as batch:
                    for idx, sq in enumerate(question_batch):
                        properties = {
                            QASchema.KNOWLEDGE_BASE_ID.value: sq.id,
                            QASchema.TOPIC.value: sq.topic,
                            QASchema.STUDY_PROGRAMS.value: sq.study_programs,
                            QASchema.QUESTION.value: sq.question,
                            QASchema.ANSWER.value: sq.answer,
                            QASchema.ORGANISATION_ID.value: sq.org_id
                        }

                        batch.add_object(properties=properties, vector=embeddings[idx])

            logging.info(f"Successfully inserted {num_questions} sample questions.")
        except Exception as e:
            logging.error(f"Failed to insert sample questions: {e}")
            raise

    def update_sample_question(self, sample_question: DatabaseSampleQuestion):
        """
        Adds a sample question to the QA collection in Weaviate.

        Args:
        - The SampleQuestion to add

        Returns:
        - None
        """
        try:
            topic = sample_question.topic
            study_programs = sample_question.study_programs
            question = sample_question.question
            answer = sample_question.answer

            # Add to QA collection in Weaviate
            embedding = self.model.embed(question)

            query_result = self.qa_collection.query.fetch_objects(
                filters=Filter.by_property(QASchema.KNOWLEDGE_BASE_ID.value).equal(sample_question.id)
            )

            if not query_result.objects:
                logging.info(f"No sample question found with knowledge_base_id: {sample_question.id}")
                return

            # Iterate through the results and update the properties
            for result in query_result.objects:
                uuid = result.uuid
                properties = result.properties
                properties[QASchema.TOPIC.value] = topic
                properties[QASchema.STUDY_PROGRAMS.value] = study_programs
                properties[QASchema.QUESTION.value] = question
                properties[QASchema.ANSWER.value] = answer

                # Reinsert the object with the updated properties
                self.qa_collection.data.update(
                    uuid=uuid,
                    properties=properties,
                    vector=embedding
                )

            logging.info(f"Updated sample question with knowledge_base_id: {sample_question.id}")
        except Exception as e:
            logging.error(f"Failed to update sample question with topic {sample_question.topic}: {e}")
            raise

    def delete_sample_questions(self, ids: List[str]):
        try:
            self.qa_collection.data.delete_many(
                where=Filter.by_property(DocumentSchema.KNOWLEDGE_BASE_ID).contains_any(ids)
            )
        except Exception as e:
            logging.error(f"Failed to batch delete sample questions: {e}")
            raise

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
    
    @staticmethod
    def remove_exact_duplicates_from_dict(dicts: List[Dict], key: str = 'content') -> list:
        """Remove dicts with duplicate values for given key, preserving order."""
        seen = set()
        deduped = []
        for d in dicts:
            val = d.get(key)
            if val not in seen:
                deduped.append(d)
                seen.add(val)
        return deduped
