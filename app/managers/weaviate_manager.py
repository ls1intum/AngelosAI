import logging
from enum import Enum
from typing import List, Union, Tuple, Dict

import weaviate
import weaviate.classes as wvc
from langchain.docstore.document import Document
from weaviate.collections import Collection
from weaviate.collections.classes.config import DataType, Configure, Property
from weaviate.collections.classes.config_vectorizers import VectorDistances
from weaviate.collections.classes.filters import Filter

from app.models.base_model import BaseModelClient
from app.models.openai_model import OpenAIModel
from app.retrieval_strategies.reranker import Reranker
from app.utils.environment import config
from app.data.user_requests import SampleQuestion, WebsiteContent


class DocumentSchema(Enum):
    """
    Schema for the embedded chunks
    """
    COLLECTION_NAME = "CITKnowledgeBase"
    STUDY_PROGRAM = "study_program"
    CONTENT = "content"
    LINK = "link"


class QASchema(Enum):
    """
    Schema for the QA Collection
    """
    COLLECTION_NAME = "QACollection"
    TOPIC = "topic"
    STUDY_PROGRAM = "study_program"
    QUESTION = "question"
    ANSWER = "answer"


class WeaviateManager:
    def __init__(self, url: str, embedding_model: BaseModelClient, reranker: Reranker):
        logging.info("Initializing Weaviate Manager")
        self.client = weaviate.connect_to_local(host=config.WEAVIATE_URL, port=config.WEAVIATE_PORT)
        self.model = embedding_model
        self.schema_initialized = False
        self.reranker = reranker
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
            ),
            Property(
                name=DocumentSchema.LINK.value,
                description="The link of the document",
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
                name=QASchema.TOPIC.value,
                description="The topic of the conversation",
                data_type=DataType.TEXT,
                index_inverted=False
            ),
            Property(
                name=QASchema.STUDY_PROGRAM.value,
                description="The study program of the student",
                data_type=DataType.TEXT,
                index_filterable=True,
                index_range_filters=True,
                index_searchable=True
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

    def get_relevant_context(self, question: str, study_program: str, language: str,
                             test_mode: bool = False) -> Union[str, Tuple[str, List[str]]]:
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
            min_relevance_score = 0.25
            if study_program.lower() != "general":
                limit = 10
                min_relevance_score = 0.15

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
            logging.info(f"No error yet after {study_program} getting relevant context")
            # documents_with_embeddings: List[DocumentWithEmbedding] = []
            # for result in query_result.objects:
            #     logging.info(
            #         f"Certainty: {result.metadata.certainty}, Score: {result.metadata.score}, Distance: {result.metadata.distance}")
            # documents_with_embeddings.append(DocumentWithEmbedding(content=result.properties['content'], embedding=result.vector['default']))

            # sorted_context = self.reranker.rerank_with_embeddings(documents_with_embeddings, keyword_string=keywords)

            context_list = [
                {
                    'content': result.properties[DocumentSchema.CONTENT.value],
                    'link': result.properties.get(DocumentSchema.LINK.value, None)
                }
                for result in query_result.objects
            ]
            content_content_list: List[str] = [doc['content'] for doc in context_list]

            # Remove exact duplicates from context_list
            content_content_list = WeaviateManager.remove_exact_duplicates(content_content_list)
            # logging.info(f"Context list length after removing exact duplicates: {len(context_list)}")

            # Rerank the unique contexts using Cohere
            sorted_context = self.reranker.rerank_with_cohere(context_list=content_content_list, query=question,
                                                              language=language,
                                                              min_relevance_score=min_relevance_score, top_n=5)
            # Integrate links
            sorted_context_with_links = []
            for sorted_content in sorted_context:
                for doc in context_list:
                    if doc['content'] == sorted_content:
                        if doc['link']:
                            sorted_context_with_links.append(f'Link: {doc["link"]}\Content: {doc["content"]}')
                        else:
                            sorted_context_with_links.append(f'Link: -\Content: {doc["content"]}')
                        break

            context = "\n-----\n".join(sorted_context_with_links)

            # Return based on test_mode
            if test_mode:
                return context, sorted_context
            else:
                return context

        except Exception as e:
            logging.error(f"Error retrieving relevant context: {e}")
            # tb = traceback.format_exc()
            # logging.error("Traceback:\n%s", tb)
            return "" if not test_mode else ("", [])

    def get_relevant_sample_questions(self, question: str, language: str) -> List[SampleQuestion]:
        """
        Retrieve relevant sample questions and answers based on the question embedding.

        Args:
            question (str): The student's question.
            language (str): The language of the question.
            top_k (int): The number of top relevant sample questions to return.

        Returns:
            List[SampleQuestion]: A list of SampleQuestion objects, sorted based on reranking results.
        """
        try:
            limit = 5
            top_n = 3
            min_relevance_score = 0.4

            # Embed the question using the embedding model
            question_embedding = self.model.embed(question)

            query_result = self.qa_collection.query.near_vector(
                near_vector=question_embedding,
                limit=limit,
                return_metadata=wvc.query.MetadataQuery(certainty=True, score=True, distance=True)
            )

            # Collect the results
            sample_questions: List[SampleQuestion] = []
            for result in query_result.objects:
                topic = result.properties.get(QASchema.TOPIC.value, "")
                retrieved_question = result.properties.get(QASchema.QUESTION.value, "")
                answer = result.properties.get(QASchema.ANSWER.value, "")
                study_program = result.properties.get(QASchema.STUDY_PROGRAM, "")
                sample_questions.append(SampleQuestion(topic=topic, question=retrieved_question, answer=answer, study_program=study_program))

            # Rerank the sample questions using the reranker
            context_list = [sq.question for sq in sample_questions]
            sorted_questions = self.reranker.rerank_with_cohere(
                context_list=context_list, query=question, language=language, top_n=top_n,
                min_relevance_score=min_relevance_score
            )

            # Map the sorted questions back to SampleQuestion objects
            sorted_sample_questions: List[SampleQuestion] = []
            for sorted_question in sorted_questions:
                for sq in sample_questions:
                    if sq.question == sorted_question:
                        sorted_sample_questions.append(sq)
                        break

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

    def add_documents(self, chunks: List[Document]):
        """
        Add chunks of Document objects to the vector database.
        """
        try:
            batch_size = 500
            num_chunks = len(chunks)
            logging.info(f"Adding {num_chunks} documents in batches of {batch_size}")

            # If using OpenAIModel, split the chunks into batches of 500
            for i in range(0, num_chunks, batch_size):
                chunk_batch = chunks[i:i + batch_size]
                if isinstance(self.model, OpenAIModel):
                    texts = [chunk.page_content for chunk in chunk_batch]
                    embeddings = self.model.embed_batch(texts)  # Embed in batch
                else:
                    # For other models, embed each chunk one at a time
                    embeddings = [self.model.embed(chunk.page_content) for chunk in chunk_batch]

                # Add the chunks to the vector database in a batch
                with self.documents.batch.rate_limit(requests_per_minute=600) as batch:
                    for index, chunk in enumerate(chunk_batch):
                        study_program = chunk.metadata.get("study_program", "general")
                        # Prepare properties
                        properties = {
                            DocumentSchema.CONTENT.value: chunk.page_content,
                            DocumentSchema.STUDY_PROGRAM.value: study_program,
                        }

                        # Add the document chunk to the batch
                        batch.add_object(properties=properties, vector=embeddings[index])

        except Exception as e:
            logging.error(f"Error adding document: {e}")

    def add_website_content(self, website_contents: List[WebsiteContent]):
        """
        Add chunks of WebsiteContent objects to the vector database, handling metadata and optional fields.
        """
        try:
            batch_size = 500
            num_chunks = len(website_contents)
            logging.info(f"Adding {num_chunks} website contents in batches of {batch_size}")

            # Split the contents into batches of 500 for embedding and adding
            for i in range(0, num_chunks, batch_size):
                content_batch = website_contents[i:i + batch_size]

                # If using OpenAIModel, embed in batches, otherwise embed one by one
                if isinstance(self.model, OpenAIModel):
                    texts = [content.content for content in content_batch]
                    embeddings = self.model.embed_batch(texts)  # Batch embed
                else:
                    embeddings = [self.model.embed(content.content) for content in content_batch]

                # Add the contents to the vector database in a batch
                with self.documents.batch.rate_limit(requests_per_minute=600) as batch:
                    for index, content in enumerate(content_batch):
                        properties = {
                            DocumentSchema.CONTENT.value: content.content,
                            DocumentSchema.STUDY_PROGRAM.value: content.study_program,
                            DocumentSchema.LINK.value: content.link
                        }

                        # Add the content chunk to the batch
                        batch.add_object(properties=properties, vector=embeddings[index])

        except Exception as e:
            logging.error(f"Error adding website content: {e}")

    def add_qa_pairs(self, qa_pairs: List[SampleQuestion]):
        """
        Adds QA pairs to the QA collection in Weaviate.

        Args:
        - qa_pairs: List of dictionaries, each containing 'topic', 'question', and 'answer' fields.

        Returns:
        - None
        """
        for qa_pair in qa_pairs:
            try:
                # Prepare the data entry for insertion
                topic = qa_pair.topic
                study_program = qa_pair.study_program
                question = qa_pair.question
                answer = qa_pair.answer

                # Add to QA collection in Weaviate
                embedding = self.model.embed(question)

                self.qa_collection.data.insert(
                    properties={
                        QASchema.TOPIC.value: topic,
                        QASchema.STUDY_PROGRAM.value: study_program,
                        QASchema.QUESTION.value: question,
                        QASchema.ANSWER.value: answer
                    },
                    vector=embedding
                )
                logging.info(f"Inserted QA pair with topic: {qa_pair.topic}")
            except Exception as e:
                logging.error(f"Failed to insert QA pair with topic {qa_pair.topic}: {e}")

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
