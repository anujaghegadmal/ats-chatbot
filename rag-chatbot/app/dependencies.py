from fastapi import Depends
from app.controllers.vector_db import VectorDBController
from app.controllers.chat import ChatController

def get_vector_db_controller() -> VectorDBController:
    return VectorDBController()

def get_chat_controller(
    vector_db: VectorDBController = Depends(get_vector_db_controller)
) -> ChatController:
    return ChatController(vector_db)