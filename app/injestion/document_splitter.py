import logging
import os
import json
from typing import List, Dict, Any

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.data.user_requests import WebsiteContent

def split_tum_documents(tum_documents: List[WebsiteContent], chunk_size: int = 1200, chunk_overlap: int = 200) -> List[WebsiteContent]:
    """
    Split TUM WebsiteContent documents using RecursiveCharacterTextSplitter into smaller chunks.
    """
    tum_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    for doc in tum_documents:
        content = doc.content
        chunks = text_splitter.split_text(content)
        
        # Create WebsiteContent chunks and preserve metadata
        for chunk in chunks:
            tum_chunks.append(WebsiteContent(
                type=doc.type,
                content=chunk,
                link=doc.link,
                study_program=doc.study_program
            ))
        logging.info(f"Split TUM document into {len(chunks)} chunks.")
    
    logging.info(f"Total TUM chunks: {len(tum_chunks)}")
    return tum_chunks

def split_pdf_documents(pdf_documents: List[Document], chunk_size: int = 1200, chunk_overlap: int = 200) -> List[Document]:
    """
    Split PDF Document objects using RecursiveCharacterTextSplitter into smaller chunks.
    """
    pdf_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    for doc in pdf_documents:
        content = doc.page_content
        chunks = text_splitter.split_text(content)
        
        # Create Document chunks and preserve metadata
        for chunk in chunks:
            pdf_chunks.append(Document(page_content=chunk, metadata=doc.metadata))
        logging.info(f"Split PDF document into {len(chunks)} chunks.")
    
    logging.info(f"Total PDF chunks: {len(pdf_chunks)}")
    return pdf_chunks

def split_cit_documents(cit_documents: List[WebsiteContent]) -> List[WebsiteContent]:
    """
    Split CIT WebsiteContent documents into smaller chunks based on a predefined separator.
    """
    cit_chunks = []
    
    for doc in cit_documents:
        sections = doc.content.split('----------------------------------------')
        for section in sections:
            section = section.strip()
            if section:
                # Create smaller WebsiteContent chunks and preserve metadata
                cit_chunks.append(WebsiteContent(
                    type=doc.type,
                    content=section,
                    link=doc.link,
                    study_program=doc.study_program
                ))
        logging.info(f"Split CIT document into {len(sections)} sections.")

    logging.info(f"Total TUM chunks: {len(cit_chunks)}")
    return cit_chunks