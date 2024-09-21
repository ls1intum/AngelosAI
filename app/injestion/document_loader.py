import logging
import os
from typing import List

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


def load_documents_from_folder(folder_path: str) -> List[Document]:
    documents = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):  # Ensure it's a file, not a directory
            if file.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                logging.info(f"Loaded {len(loaded_docs)} pages from .pdf file: {file}")
            elif file.lower().endswith(".txt"):
                with open(file_path, 'r') as f:
                    content = f.read()
                    document = Document(page_content=content, metadata={"source": file_path})
                    documents.append(document)
                logging.info(f"Loaded .txt file: {file}")
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    other_documents = []
    txt_documents = []
    logging.info(f"Splitting {len(documents)} documents")
    
    # Separate documents based on the file type in the metadata
    for doc in documents:
        if doc.metadata.get("source", "").lower().endswith(".txt"):
            txt_documents.append(doc)
        else:
            other_documents.append(doc)
    
    # Apply different splitting strategies for PDF and TXT documents
    logging.info(f"Splitting {len(documents)} documents")
    chunks = split_documents_recursive(other_documents)
    txt_chunks = split_cit_txt_documents(txt_documents)
    return chunks + txt_chunks


def split_documents_recursive(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    return splitter.split_documents(documents)


def split_cit_txt_documents(documents: List[Document]) -> List[Document]:
    processed_documents = []  
    for doc in documents:
        sections = doc.page_content.split('----------------------------------------')
        logging.info(f"TXT Document split in {len(sections)} sections")
        for section in sections:
            section = section.strip()
            if section:
                processed_documents.append(Document(page_content=section, metadata=doc.metadata))
    return processed_documents