import logging
import os

from app.managers.weaviate_manager import WeaviateManager
from app.utils.document_loader import load_documents_from_folder, split_documents


def initialize_vectorstores(base_folder: str, weaviate_manager: WeaviateManager):
    """
    Initializes vector stores by adding documents to Weaviate with their embeddings.

    Args:
    - base_folder: Path to the base folder containing general and program-specific documents.
    - weaviate_manager: Instance of WeaviateManager to manage embeddings and document insertion.

    Returns:
    - None (documents and embeddings are inserted into Weaviate).
    """
    logging.info("Initializing vector stores...")
    general_docs = load_documents_from_folder(base_folder)

    # Split the documents into chunks
    general_chunks = split_documents(general_docs)

    logging.info("Start with embeddings")
    for chunk in general_chunks:
        weaviate_manager.add_document(chunk.page_content, "general")  # 'general' classification

    # Repeat for program-specific documents
    for subdir in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subdir)
        if os.path.isdir(subfolder_path):
            program_docs = load_documents_from_folder(subfolder_path)
            program_chunks = split_documents(program_docs)

            for chunk in program_chunks:
                weaviate_manager.add_document(chunk.page_content, subdir)  # Use subfolder name as classification

    print("Vector stores initialized and documents saved to Weaviate.")
