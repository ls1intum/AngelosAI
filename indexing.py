import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document  # Import the Document class

def initialize_vectorstores(base_folder, openai_api_key):
    """
    Initializes vector stores for general and program-specific documents.
    
    Args:
    - base_folder: The folder containing general and program-specific subfolders.
    - openai_api_key: The OpenAI API key for embeddings.
    
    Returns:
    - A dictionary of vector stores with collection names.
    """
    # Initialize the vector stores
    vectorstores = {}

    # Create an embedding instance
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Recursive text splitter for chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)

    # Helper function to load documents (txt, pdf)
    def load_documents_from_folder(folder_path):
        documents = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".pdf"):
                    # Load PDFs
                    loader = PyPDFLoader(file_path)
                    loaded_docs = loader.load()
                    documents.extend(loaded_docs)  # PDFs are already loaded as Document objects
                    logging.info(f"Loaded {len(loaded_docs)} pages from {file}")
                elif file.endswith(".txt"):
                    # Load TXT files and convert to Document objects
                    with open(file_path, 'r') as f:
                        content = f.read()
                        # Wrap the text content in a Document object
                        document = Document(page_content=content, metadata={"source": file_path})
                        documents.append(document)
                    logging.info(f"Loaded TXT file {file}")
        return documents

    # Load general documents
    general_docs = load_documents_from_folder(base_folder)
    
    # Split the documents
    general_chunks = text_splitter.split_documents(general_docs)

    # Create a vector store for general documents
    general_vectorstore = Chroma.from_documents(
        documents=general_chunks,
        embedding=embeddings,
        collection_name="general"
    )
    vectorstores["general"] = general_vectorstore
    logging.info(f"General vectorstore created with {len(general_vectorstore.get()['documents'])} chunks.")

    text_splitter2 = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Load program-specific documents
    for subdir in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subdir)
        if os.path.isdir(subfolder_path):
            program_docs = load_documents_from_folder(subfolder_path)
            
            # Split the program-specific documents
            program_chunks = text_splitter2.split_documents(program_docs)

            # Create a vector store for each study program
            program_vectorstore = Chroma.from_documents(
                documents=program_chunks,
                embedding=embeddings,
                collection_name=subdir  # Use the subfolder name as the collection name
            )
            vectorstores[subdir] = program_vectorstore
            logging.info(f"Vectorstore created for '{subdir}' with {len(program_vectorstore.get()['documents'])} chunks.")
    
    return vectorstores