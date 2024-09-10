import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import logging


def load_documents_from_folder(folder_path: str):
    documents = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                logging.info(f"Loaded {len(loaded_docs)} pages from {file}")
            elif file.endswith(".txt"):
                with open(file_path, 'r') as f:
                    content = f.read()
                    document = Document(page_content=content, metadata={"source": file_path})
                    documents.append(document)
                logging.info(f"Loaded TXT file {file}")
    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    return splitter.split_documents(documents)
