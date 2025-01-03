import logging
import os
import json
from typing import List, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentSplitter:
    def split_cit_content(self, content: str):
        result: List[str] = []
        sections = content.split('----------------------------------------')
        for section in sections:
            section = section.strip()
            if section:
                result.append(section)
        return result
    
    def split_tum_content(self, content: str, chunk_size: int = 1200, chunk_overlap: int = 200):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_text(content)
        return chunks
    
    def split_pdf_document(self, content: str, chunk_size: int = 1200, chunk_overlap: int = 200):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_text(content)
        return chunks