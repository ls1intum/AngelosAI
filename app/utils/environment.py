import os
from app.models.ollama_model import OllamaModel
from app.models.openai_model import OpenAIModel


def get_model():
    """Select and return the appropriate model based on environment configuration."""
    use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"

    if use_ollama:
        ollama_url = os.getenv("GPU_URL")
        model = os.getenv("OLLAMA_MODEL")
        embed_model = os.getenv("EMBED_MODEL")
        return OllamaModel(model, ollama_url, embed_model)
    else:
        api_key = os.getenv("LLAMA_MODEL_TOKEN")
        url = os.getenv("LLAMA_MODEL_URI")
        return OpenAIModel(api_key, url)