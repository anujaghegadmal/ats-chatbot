from pydantic import BaseModel

class WeaviateDocument(BaseModel):
    doc_id: str
    content: str
    embedding: list[float]
    metadata: dict

    