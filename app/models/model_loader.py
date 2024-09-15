import logging

from app.models.ollama_model import OllamaModel
from app.models.openai_model import OpenAIModel
from app.utils.environment import config


def get_model():
    """Select and return the appropriate model based on environment configuration."""
    logging.info('Getting model')
    use_ollama = config.USE_OLLAMA.lower() == "true"
    if use_ollama:
        logging.info("Using ollama as model")
        return OllamaModel(config.MODEL, config.OLLAMA_URL, config.EMBED_MODEL)
    else:
        logging.info("Using OpenAI as model")
        return OpenAIModel(config.OPENAI_API_KEY, config.URL)
