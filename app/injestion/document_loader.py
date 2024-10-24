import logging
import os
import json
from typing import List, Dict, Any

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.data.user_requests import SampleQuestion, WebsiteContent


def load_pdf_documents_from_folder(base_folder: str, study_program: str = "general") -> List[Document]:
    """
    Traverse the base folder and all its subfolders to find and load PDF files into Document objects.
    Attach the study program (subfolder name) to the Document metadata.

    Args:
    - base_folder: Path to the base folder containing PDF files and subfolders.
    - study_program: Name of the study program (subfolder name).

    Returns:
    - A list of Document objects parsed from the PDF files.
    """
    documents: List[Document] = []

    # Go through each subdirectory and file in the base folder
    for subdir in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subdir)

        # If the current path is a directory, recurse into it
        if os.path.isdir(subfolder_path):
            # Use the folder name as the study program when recursing into the subfolder
            new_study_program = subdir
            documents.extend(load_pdf_documents_from_folder(subfolder_path, new_study_program))
        
        # If it's a file and ends with .pdf, process it
        elif subdir.lower().endswith(".pdf"):
            file_path = os.path.join(base_folder, subdir)
            try:
                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()

                # Attach the study program name to each document's metadata
                for doc in loaded_docs:
                    doc.metadata["study_program"] = study_program
                    doc.metadata["source"] = file_path

                documents.extend(loaded_docs)
                logging.info(f"Loaded {len(loaded_docs)} pages from .pdf file: {file_path} under study program: {study_program}")
            except Exception as e:
                logging.error(f"Failed to load PDF file {file_path}: {e}")

    return documents

def load_qa_pairs_from_folder(qa_folder: str) -> List[SampleQuestion]:
    """
    Reads JSON files from the qa_folder and extracts QA pairs.

    Args:
    - qa_folder: Path to the folder containing JSON QA files.

    Returns:
    - List of QA pairs, each represented as an instance of SampleQuestion with 'topic', 'question', and 'answer'.
    """
    qa_pairs: List[SampleQuestion] = []

    for file_name in os.listdir(qa_folder):
        file_path = os.path.join(qa_folder, file_name)
        if file_name.endswith(".json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data: Dict[str, Any] = json.load(file)

                    # Default values and type validation
                    topic = data.get("topic", "Unknown Topic")
                    study_program = data.get("study_program", "general")
                    correspondence = data.get("correspondence", [])

                    if not isinstance(correspondence, list):
                        logging.warning(f"Unexpected format in file: {file_path}")
                        continue

                    question, answer = None, None
                    for entry in correspondence:
                        if isinstance(entry, dict):
                            sender = entry.get("sender")
                            message = entry.get("message", "")
                            order_key = entry.get("orderKey")
                            if sender == "STUDENT" and order_key == 0:
                                question = message
                            elif sender == "AA" and order_key == 1:
                                answer = message

                    if question and answer:
                        # Append a new SampleQuestion object to the list
                        qa_pairs.append(SampleQuestion(
                            topic=topic,
                            question=question,
                            answer=answer,
                            study_program=study_program
                        ))
                    else:
                        logging.error(f"Failed to parse JSON file {file_name}")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logging.error(f"Failed to load file {file_name}: {e}")

    logging.info(f"Loaded {len(qa_pairs)} QA pairs from folder: {qa_folder}")
    return qa_pairs

def load_website_content_from_folder(base_folder: str) -> List[WebsiteContent]:
    """
    Traverse through the base folder and all subfolders to find and load JSON files
    and convert them into WebsiteContent objects.
    
    Args:
    - base_folder: Path to the base folder containing JSON files and subfolders.
    
    Returns:
    - A list of WebsiteContent objects parsed from the JSON files.
    """
    website_contents: List[WebsiteContent] = []
    
    # Traverse the base folder and all its subfolders
    for root, _, files in os.walk(base_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Validate if necessary fields are present
                        if "type" in data and "content" in data and "link" in data and "study_program" in data:
                            content_object = WebsiteContent(
                                type=data["type"],
                                content=data["content"],
                                link=data["link"],
                                study_program=data["study_program"]
                            )
                            website_contents.append(content_object)
                            logging.info(f"Loaded WebsiteContent from {file_path}")
                        else:
                            logging.warning(f"Missing required fields in JSON file: {file_path}")
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    logging.error(f"Failed to load file {file_path}: {e}")

    logging.info(f"Total WebsiteContent objects loaded: {len(website_contents)}")
    return website_contents