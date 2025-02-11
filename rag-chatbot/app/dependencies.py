from fastapi import Depends
from weaviate import Client, AuthApiKey
# from app.controllers.vector_db import VectorDBController
# from app.controllers.chat import ChatController
from app.config import settings
from app.controllers.upload_pdf import PDFController

# def get_vector_db_controller() -> VectorDBController:
#     return VectorDBController()

# def get_chat_controller(
#     vector_db: VectorDBController = Depends(get_vector_db_controller)
# ) -> ChatController:
#     return ChatController(vector_db)

def get_weaviate_client():
    client = Client(
        url=settings.weaviate_url,
        auth_client_secret=AuthApiKey(settings.weaviate_api_key),
        additional_headers={'X-Cohere-Api-Key': settings.cohere_api_key}
    )
    return client

def get_pdf_controller(weaviate_client=Depends(get_weaviate_client)) -> PDFController:
    return PDFController(weaviate_client)
