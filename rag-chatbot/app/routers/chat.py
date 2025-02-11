from fastapi import APIRouter, Depends, HTTPException
from app.controllers.chat import ChatController
from app.schemas.chat import Message, ChatWithMessages, ChatRequest
from app.database import db
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime
from typing import List
from app.schemas.user import User
from app.schemas.chat import Chat, Message, ChatWithMessages , CreateChatRequest , Message, CreateMessageRequest
from app.database import messages_collection, chats_collection
router = APIRouter()
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import app
# Security and authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

@router.post("/chats", response_model=Chat)
async def create_chat(chat_request: CreateChatRequest, current_user: User = Depends(get_current_user)):
    if current_user["user_id"] != chat_request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create a chat for this user")

    chat_id = str(ObjectId())  # Generate a unique chat ID
    chat_data = {
        "chat_id": chat_id,
        "user_id": chat_request.user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.chats.insert_one(chat_data)
    return chat_data

@router.get("/chats/{user_id}", response_model=List[Chat])
async def get_chats(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access chats for this user")

    chats = await db.chats.find({"user_id": user_id}).to_list(None)
    return chats

@router.post("/chats/{chat_id}/messages", response_model=Message)
async def add_message(
    chat_id: str,
    message_request: CreateMessageRequest,  # Use the request body model
    current_user: User = Depends(get_current_user)
):
    if current_user["user_id"] != message_request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add a message to this chat")

    # Generate message_id and timestamp on the server side
    message_data = {
        "message_id": str(ObjectId()),  # Generate a unique message ID
        "chat_id": chat_id,  # Add the chat_id from the URL
        "user_id": message_request.user_id,
        "role": message_request.role,
        "content": message_request.content,
        "timestamp": datetime.utcnow()  # Add the current timestamp
    }

    # Insert the message into the database
    await messages_collection.insert_one(message_data)

    # Update the chat's updated_at timestamp
    await chats_collection.update_one({"chat_id": chat_id}, {"$set": {"updated_at": datetime.utcnow()}})

    return message_data

@router.get("/chats/{chat_id}/messages", response_model=List[Message])
async def get_messages(chat_id: str, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if current_user["user_id"] != chat["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")

    messages = await db.messages.find({"chat_id": chat_id}).to_list(None)
    return messages

@router.get("/chats/{chat_id}/full", response_model=ChatWithMessages)
async def get_chat_with_messages(chat_id: str, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if current_user["user_id"] != chat["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")

    messages = await db.messages.find({"chat_id": chat_id}).to_list(None)
    return {"chat": chat, "messages": messages}
