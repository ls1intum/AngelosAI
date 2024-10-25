import logging

from app.models.azure_openai_model import AzureOpenAIModel
from app.models.base_model import BaseModelClient
from app.models.ollama_model import OllamaModel
from app.models.openai_model import OpenAIModel
from app.utils.environment import config


def get_model() -> BaseModelClient:
    """Select and return the appropriate model based on environment configuration."""
    logging.info('Getting model')
    use_ollama = config.USE_OLLAMA.lower() == "true"
    if not use_ollama:
        if not config.USE_AZURE == "true":
            logging.info("Using OpenAI as model")
            return OpenAIModel(model=config.OPENAI_MODEL, embed_model=config.OPENAI_EMBEDDING_MODEL,
                               api_key=config.OPENAI_API_KEY)
        else:
            logging.info("Using OpenAI hosted on azure as model")
            return AzureOpenAIModel(model=config.OPENAI_MODEL, embed_model=config.OPENAI_EMBEDDING_MODEL,
                                    azure_deployment=config.OPENAI_MODEL_DEPLOYMENT,
                                    api_key=config.AZURE_OPENAI_API_KEY)
    else:
        logging.info(f"Using ollama as model: {config.GPU_MODEL} ")
        if not config.GPU_MODEL:
            logging.error("No config gpu model")
        return OllamaModel(model=config.GPU_MODEL, embed_model=config.EMBED_MODEL, url=config.GPU_URL)
