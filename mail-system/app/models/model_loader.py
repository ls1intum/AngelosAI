from app.common.environment import config
from app.models.base_model import BaseModelClient
from app.models.local_model import LocalBaseModel
from app.models.ollama_model import OllamaModel
from app.models.openai_azure_model import AzureOpenAIBaseModel
from app.models.openai_model import OpenAIBaseModel

default_model_name = "llama3.1:70b"


def get_model_client() -> BaseModelClient:
    use_openai = config.USE_OPENAI.lower() == "true"
    local = config.USE_LOCAL_MODEL.lower() == "true"
    if local:
        return LocalBaseModel(model=config.LOCAL_MODEL,
                              api_key=config.LOCAL_API_KEY, endpoint=config.LOCAL_ENDPOINT)
    elif use_openai:
        if not config.USE_AZURE == "true":
            return OpenAIBaseModel(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
        else:
            return AzureOpenAIBaseModel(model=config.OPENAI_MODEL, azure_version=config.AZURE_VERSION,
                                        api_key=config.OPENAI_API_KEY, azure_endpoint=config.AZURE_ENDPOINT)
    else:
        return OllamaModel(model=config.GPU_MODEL, url=config.GPU_URL)
