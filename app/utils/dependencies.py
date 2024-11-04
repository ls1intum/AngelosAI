from app.managers.request_handler import RequestHandler
from app.managers.weaviate_manager import WeaviateManager
from app.managers.auth_handler import AuthHandler
from app.retrieval_strategies.reranker import Reranker
from app.models.model_loader import get_model
from app.prompt.prompt_manager import PromptManager
from app.utils.environment import config

# Initialize resources  
model = get_model()
reranker = Reranker(model=model, api_key_en=config.COHERE_API_KEY_EN, api_key_multi=config.COHERE_API_KEY_MULTI)
weaviate_manager = WeaviateManager(config.WEAVIATE_URL, embedding_model=model, reranker=reranker)
prompt_manager = PromptManager()
request_handler = RequestHandler(weaviate_manager=weaviate_manager, model=model, prompt_manager=prompt_manager)
auth_handler = AuthHandler(angelos_api_key=config.ANGELOS_APP_API_KEY, secret_key=config.API_ENDPOINT_KEY, algorithm=config.ALGORITHM, access_token_expires_minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

# Provide a shutdown mechanism for the model
def shutdown_model():
    model.close_session()
