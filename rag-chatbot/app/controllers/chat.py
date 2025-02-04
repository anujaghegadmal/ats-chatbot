import os
from openai import OpenAI
from app.controllers.vector_db import VectorDBController
from app.models.mongo.message import Message
from app.schemas.chat import ChatRequest, ChatResponse

class ChatController:
    def __init__(self, vector_db: VectorDBController):
        self.vector_db = vector_db
        self.gpt = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        context = await self.vector_db.search_documents(request.message)
        prompt = self._build_prompt(request.message, context)
        response = await self.get_chat_response(prompt)
        
        await Message(
            content=request.message,
            sender="user",
            conversation_id=request.conversation_id
        ).insert()
        
        return ChatResponse(response=response)
    
    async def get_chat_response(self, prompt):
        response = self.gpt.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def _build_prompt(self, message: str, context: list[str]) -> str:
        return f"Context: {context}\n\nQuestion: {message}\nAnswer:"
