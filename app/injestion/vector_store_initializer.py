import logging
import os
from typing import List
from langchain.docstore.document import Document

from app.injestion.document_loader import load_website_content_from_folder, load_pdf_documents_from_folder, load_qa_pairs_from_folder
from app.injestion.document_splitter import split_cit_documents, split_tum_documents, split_pdf_documents
from app.managers.weaviate_manager import WeaviateManager
from app.utils.environment import config
from app.data.user_requests import SampleQuestion, WebsiteContent


def initialize_vectorstores(base_folder: str, qa_folder: str, weaviate_manager: WeaviateManager):
    """
    Initializes vector stores by adding documents to Weaviate with their embeddings.

    Args:
    - base_folder: Path to the base folder containing general and program-specific documents.
    - weaviate_manager: Instance of WeaviateManager to manage embeddings and document insertion.

    Returns:
    - None (documents and embeddings are inserted into Weaviate).
    """
    delete_before_init = config.DELETE_BEFORE_INIT.lower() == "true"

    # Delete existing data if the DELETE_BEFORE_INIT is set to true
    if delete_before_init:
        logging.warning("Deleting existing data before initialization...")
        weaviate_manager.delete_collections()
        weaviate_manager.initialize_schema()
        weaviate_manager.initialize_qa_schema()
    else:
        logging.info("Skipping data deletion...")

    logging.info("Initializing vector stores...")

    # Process QA pairs
    qa_pairs: List[SampleQuestion] = load_qa_pairs_from_folder(qa_folder)
    weaviate_manager.add_qa_pairs(qa_pairs)

    # PDF files
    pdf_docs: List[Document] = load_pdf_documents_from_folder(base_folder)
    pdf_docs_split: List[Document] = split_pdf_documents(pdf_documents=pdf_docs)
    weaviate_manager.add_documents(pdf_docs_split)

    # Website content
    website_content: List[WebsiteContent] = load_website_content_from_folder(base_folder)
    cit_content = [content for content in website_content if content.type == "CIT"]
    tum_content = [content for content in website_content if content.type == "TUM"]
    cit_chunks = split_cit_documents(cit_content)
    tum_chunks = split_tum_documents(tum_content)
    split_website_content: List[WebsiteContent] = cit_chunks + tum_chunks
    weaviate_manager.add_website_content(split_website_content)

    logging.info("Vector stores initialized and documents saved to Weaviate.")
