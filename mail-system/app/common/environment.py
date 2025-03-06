import os

from dotenv import load_dotenv

if os.getenv("ENVIRONMENT") == "development":
    load_dotenv("./development.env")


class Config:
    # email
    IMAP_SERVER = os.getenv("IMAP_SERVER")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    IMAP_PORT = os.getenv("IMAP_PORT")
    SMTP_PORT = os.getenv("SMTP_PORT")

    # appliocation flow
    USE_OPENAI = os.getenv("USE_OPENAI", "false")
    USE_AZURE = os.getenv("USE_AZURE", "false")

    # gpu
    GPU_USER = os.getenv("GPU_USER")
    GPU_PASSWORD = os.getenv("GPU_PASSWORD")
    GPU_HOST = os.getenv("GPU_HOST")
    GPU_MODEL = os.getenv("GPU_MODEL")
    GPU_URL = os.getenv("GPU_URL")

    USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "false")
    LOCAL_API_KEY = os.getenv("LOCAL_API_KEY", "lm-studio")
    LOCAL_MODEL = os.getenv("LOCAL_MODEL")
    LOCAL_EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL")
    LOCAL_ENDPOINT = os.getenv("LOCAL_ENDPOINT")

    # test
    TEST_EML_PATH = os.getenv("TEST_EML_PATH")

    # angelos
    ANGELOS_URL = os.getenv("ANGELOS_URL")
    ANGELOS_APP_API_KEY = os.getenv("ANGELOS_APP_API_KEY")

    # openai
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
    AZURE_VERSION = os.getenv("OPENAI_VERSION")


config = Config()
