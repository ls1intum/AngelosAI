import logging
import os

from app.injestion.document_loader import load_documents_from_folder, split_documents, load_qa_pairs_from_folder
from app.managers.weaviate_manager import WeaviateManager
from app.utils.environment import config


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
    qa_pairs = load_qa_pairs_from_folder(qa_folder)
    weaviate_manager.add_qa_pairs(qa_pairs)

    general_docs = load_documents_from_folder(base_folder)

    # Split the documents into chunks
    general_chunks = split_documents(general_docs)

    logging.info(f"Start with general embeddings {len(general_chunks)}")
    weaviate_manager.add_documents(general_chunks, "general")  # 'general' classification

    logging.info("Start with specific embeddings")

    # Repeat for program-specific documents
    for subdir in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subdir)
        if os.path.isdir(subfolder_path):
            program_docs = load_documents_from_folder(subfolder_path)
            program_chunks = split_documents(program_docs)
            logging.info(f"Start with specific embeddings: {subdir} and chunks: {len(program_chunks)}")
            weaviate_manager.add_documents(program_chunks, subdir)

    logging.info("Vector stores initialized and documents saved to Weaviate.")
