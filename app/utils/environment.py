import os

from dotenv import load_dotenv

load_dotenv("./../development.env")


class Config:
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "localhost")
    WEAVIATE_PORT = os.getenv("WEAVIATE_PORT", "8001")
    KNOWLEDGE_BASE_FOLDER = os.getenv("KNOWLEDGE_BASE_FOLDER", "./knowledge/documents")
    QA_FOLDER = os.getenv("QA_FOLDER", "./knowledge/sample-correspondences")
    DELETE_BEFORE_INIT = os.getenv("DELETE_BEFORE_INIT", "false")
    USE_OLLAMA = os.getenv("USE_OLLAMA", "true")
    USE_AZURE = os.getenv("USE_AZURE", "true")
    OLLAMA_URL = os.getenv("GPU_URL")
    EMBED_MODEL = os.getenv("EMBED_MODEL")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
    API_KEY = os.getenv("LLAMA_MODEL_TOKEN")
    URL = os.getenv("LLAMA_MODEL_URI")
    GPU_USER = os.getenv("GPU_USER")
    GPU_PASSWORD = os.getenv("GPU_PASSWORD")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    GPU_MODEL = os.getenv("OLLAMA_MODEL")
    GPU_HOST = os.getenv("GPU_HOST")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    TEST_MODE = os.getenv("TEST_MODE")
    OPENAI_MODEL_DEPLOYMENT = os.getenv("OPENAI_MODEL_DEPLOYMENT")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")


config = Config()
