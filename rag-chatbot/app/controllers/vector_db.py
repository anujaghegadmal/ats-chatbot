import weaviate
import openai
import json
from app.config import settings
from app.models.weaviate.document import WeaviateDocument

class VectorDBController:
    def __init__(self):
        self.client = weaviate.Client(
            url=settings.weaviate_url,
            additional_headers={"X-OpenAI-Api-Key": settings.openai_api_key}
        )
        self.embedder = openai.OpenAI(api_key=settings.openai_api_key)
    
    def _generate_embedding(self, text: str) -> list[float]:
        response = self.embedder.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding if response.data else []
    
    def store_document(self, doc_id: str, content: str, metadata: dict = {}):
        vector = self._generate_embedding(content)
        self.client.data_object.create(
            class_name="Document",
            data={"content": content, "metadata": json.dumps(metadata)},
            vector=vector,
            uuid=doc_id
        )
    
    async def search_documents(self, query: str, k: int = 3) -> list[str]:
        try:
            vector = self._generate_embedding(query)
            result = self.client.query.get(
                "Document", ["content"]
            ).with_near_vector({"vector": vector}).with_limit(k).do()
            
            return [item["content"] for item in result["data"]["Get"]["Document"]]
        except Exception as e:
            print(f"Vector search error: {e}")
            return []