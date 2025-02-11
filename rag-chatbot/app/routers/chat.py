from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest
from app.controllers.chat import ChatController

router = APIRouter()

@router.post("/send_message")
async def send_message(
    request: ChatRequest, 
    controller: ChatController = Depends(ChatController)
):
    print("hit from chat router", request.message)
    try:
        result = await controller.process_user_message(request.message)
        return {"message": "Message sent", "content": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))