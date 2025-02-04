from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.dependencies import get_chat_controller
from app.controllers.chat import ChatController

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    return await controller.process_message(request)