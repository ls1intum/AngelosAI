import os
import logging

from dotenv import load_dotenv

load_dotenv(".env")

class Config:
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "localhost")
    WEAVIATE_PORT = os.getenv("WEAVIATE_PORT", "8001")
    KNOWLEDGE_BASE_FOLDER = os.getenv("KNOWLEDGE_BASE_FOLDER", "./knowledge")
    DELETE_BEFORE_INIT = os.getenv("DELETE_BEFORE_INIT", "false")
    USE_OLLAMA = os.getenv("USE_OLLAMA", "true")
    OLLAMA_URL = os.getenv("GPU_URL")
    MODEL = os.getenv("OLLAMA_MODEL")
    EMBED_MODEL = os.getenv("EMBED_MODEL")
    API_KEY = os.getenv("LLAMA_MODEL_TOKEN")
    URL = os.getenv("LLAMA_MODEL_URI")
    GPU_USER = os.getenv("GPU_USER")
    GPU_PASSWORD = os.getenv("GPU_PASSWORD")
    GPU_HOST = os.getenv("GPU_HOST")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TEST_MODE = os.getenv("TEST_MODE")


config = Config()
