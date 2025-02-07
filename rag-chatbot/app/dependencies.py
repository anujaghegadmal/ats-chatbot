from fastapi import Depends
from weaviate.classes.init import Auth
from app.controllers.vector_db import VectorDBController
from app.controllers.chat import ChatController
import weaviate
from app.config import settings
from app.controllers.upload_pdf import PDFController

def get_vector_db_controller() -> VectorDBController:
    return VectorDBController()

def get_chat_controller(
    vector_db: VectorDBController = Depends(get_vector_db_controller)
) -> ChatController:
    return ChatController(vector_db)

def get_weaviate_client():
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=settings.weaviate_url,
        auth_credentials=Auth.api_key(settings.weaviate_api_key),
        headers={'X-OpenAI-Api-key': settings.openai_api_key}
    )
    return client

def get_pdf_controller(weaviate_client=Depends(get_weaviate_client)) -> PDFController:
    return PDFController(weaviate_client)
