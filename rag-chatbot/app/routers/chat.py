# from fastapi import APIRouter, Depends
# from app.schemas.chat import ChatRequest, ChatResponse
# from app.dependencies import get_vector_db_controller
# from app.controllers.chat import ChatController
# from app.controllers.vector_db import VectorDBController

# router = APIRouter()

# # @router.get("/retrieve_documents/")
# # async def retrieve_documents(vector_db: VectorDBController = Depends(get_vector_db_controller)):
# #     documents = vector_db.query_with_graphql()
# #     return {"documents": documents}