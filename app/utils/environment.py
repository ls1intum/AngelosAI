import os

from dotenv import load_dotenv

if os.getenv("ENVIRONMENT") == "development":
    load_dotenv("./../development.env")


class Config:
    # Weaviate Database
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "localhost")
    WEAVIATE_PORT = os.getenv("WEAVIATE_PORT", "8001")
    # Knowledge base folders (TODO: Remove)
    KNOWLEDGE_BASE_FOLDER = os.getenv("KNOWLEDGE_BASE_FOLDER", "./knowledge/documents")
    QA_FOLDER = os.getenv("QA_FOLDER", "./knowledge/sample-correspondences")
    # Development config
    TEST_MODE = os.getenv("TEST_MODE")
    DELETE_BEFORE_INIT = os.getenv("DELETE_BEFORE_INIT", "false")
    # Ollama
    USE_OLLAMA = os.getenv("USE_OLLAMA", "false")
    GPU_URL = os.getenv("GPU_URL")
    GPU_USER = os.getenv("GPU_USER")
    GPU_PASSWORD = os.getenv("GPU_PASSWORD")
    GPU_MODEL = os.getenv("GPU_MODEL")
    GPU_EMBED_MODEL = os.getenv("GPU_EMBED_MODEL")
    GPU_HOST = os.getenv("GPU_HOST")
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
    # Azure OpenAI
    USE_AZURE = os.getenv("USE_AZURE", "true")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")
    # Cohere
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    COHERE_API_KEY_MULTI = os.getenv("COHERE_API_KEY_MULTI")
    COHERE_API_KEY_EN = os.getenv("COHERE_API_KEY_EN")
    # Safeguard
    API_ENDPOINT_KEY = os.getenv("API_ENDPOINT_KEY")
    ANGELOS_APP_API_KEY = os.getenv("ANGELOS_APP_API_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    MAX_MESSAGE_LENGTH = 3000
    EXPECTED_USERNAME = os.getenv("EXPECTED_USERNAME")
    EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD")
    WIRHOUT_USER_LOGIN = os.getenv("WIRHOUT_USER_LOGIN")


config = Config()
