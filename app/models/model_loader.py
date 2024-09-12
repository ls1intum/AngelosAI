from app.models.ollama_model import OllamaModel
from app.models.openai_model import OpenAIModel
from app.utils.environment import config


def get_model():
    """Select and return the appropriate model based on environment configuration."""
    use_ollama = config.USE_OLLAMA.lower() == "true"
    if use_ollama:
        return OllamaModel(config.MODEL, config.OLLAMA_URL, config.EMBED_MODEL)
    else:
        return OpenAIModel(config.API_KEY, config.URL)
