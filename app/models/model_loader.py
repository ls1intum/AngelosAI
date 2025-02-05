import logging

from app.models.azure_openai_model import AzureOpenAIModel
from app.models.base_model import BaseModelClient
from app.models.local_model import LocalModel
from app.models.ollama_model import OllamaModel
from app.models.openai_model import OpenAIModel
from app.utils.environment import config


def get_model() -> BaseModelClient:
    """Select and return the appropriate model based on environment configuration."""
    logging.info('Getting model')
    use_ollama = config.USE_OLLAMA.lower() == "true"
    local = config.USE_LOCAL_MODEL.lower() == "true"
    logging.info(f"{config.LOCAL_ENDPOINT} is the endpoint")
    if local:
        logging.info("Using local model")
        return LocalModel(model=config.LOCAL_MODEL, embed_model=config.LOCAL_EMBED_MODEL,
                          api_key=config.LOCAL_API_KEY, endpoint=config.LOCAL_ENDPOINT)

    elif not use_ollama:
        if not config.USE_AZURE == "true":
            logging.info("Using OpenAI as model")
            return OpenAIModel(model=config.OPENAI_MODEL, embed_model=config.OPENAI_EMBEDDING_MODEL,
                               api_key=config.OPENAI_API_KEY)
        else:
            logging.info("Using OpenAI hosted on Azure as model")
            return AzureOpenAIModel(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                model=config.AZURE_OPENAI_DEPLOYMENT,
                embed_model=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            )
    else:
        logging.info(f"Using ollama as model: {config.GPU_MODEL} ")
        if not config.GPU_MODEL:
            logging.error("No config gpu model")
        return OllamaModel(model=config.GPU_MODEL, embed_model=config.GPU_EMBED_MODEL, url=config.GPU_URL)
