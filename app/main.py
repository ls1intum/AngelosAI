import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.question_router import router as question_router
from app.managers.request_handler import RequestHandler
from app.managers.weaviate_manager import WeaviateManager
from app.prompt.prompt_manager import PromptManager
from app.utils.environment import get_model
from app.utils.setup_logging import setup_logging
from app.utils.vector_store_initializer import initialize_vectorstores

setup_logging()
logging.info("Starting application...")
load_dotenv("./../development.env")
# app = FastAPI()
model = get_model()
model.embed("""Sehr geehrte Damen und Herren, 

mein Name ist Mohamed firas boufaden und ich bin Student der Informatik (Bsc). 
Mir wurde ein Urlaubsemester für diese Semester(SoS2024) gewährt, und ich habe hierzu einige Fragen bezüglich meiner Prüfungen. 

Habe ich das Recht, Prüfungen während des Endterm oder nur in der Kontrollphase abzulegen, obwohl ich mich im Urlaubsemester befinde? 
Falls ich für die Prüfungen angemeldet bin, muss ich mich von diesen Prüfungen abmelden? 
Muss ich die Prüfungen ausschließlich in der Kontrollphase ablegen? 

Ich bedanke mich im Voraus für Ihre Hilfe und freue mich auf Ihre baldige Antwort. 

Mit freundlichen Grüßen,
Mohamed firas boufaden
Matrk-Nr:03752059
""")
# prompt_manager = PromptManager()
# print(f"url {os.getenv("WEAVIATE_URL")}")
# weaviate_manager = WeaviateManager(os.getenv("WEAVIATE_URL"), model)
# question_handler = RequestHandler(weaviate_manager, prompt_manager)
# initialize_vectorstores(os.getenv("KNOWLEDGE_BASE_FOLDER"), weaviate_manager)
# app.include_router(router=question_router)
