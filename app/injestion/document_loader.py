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
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                logging.info(f"Loaded {len(loaded_docs)} pages from .pdf file: {file}")
            elif file.endswith(".txt"):
                with open(file_path, 'r') as f:
                    content = f.read()
                    document = Document(page_content=content, metadata={"source": file_path})
                    documents.append(document)
                logging.info(f"Loaded .txt file: {file}")
    return documents


def split_documents(documents) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    return splitter.split_documents(documents)
