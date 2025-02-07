import os
import shutil
import fitz  # PyMuPDF for extracting text from PDFs
from sentence_transformers import SentenceTransformer

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class PDFController:
    def __init__(self, weaviate_client):
        self.client = weaviate_client

    def __del__(self):
        """Ensures Weaviate connection is closed properly."""
        if hasattr(self, "client") and self.client:
            self.client.close()

    async def process_pdf(self, file) -> dict:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Saving the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extracting text
        extracted_text = self.extract_text_from_pdf(file_path)

        # Generating embeddings
        embedding = self.generate_embedding(extracted_text)

        # Storing in Weaviate
        self.store_text_in_weaviate(extracted_text, embedding, file.filename)

        return {"message": "File uploaded and processed successfully."}

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text("text") for page in doc)

    def generate_embedding(self, text: str):
        """Generating embeddings using Sentence Transformers."""
        return embedding_model.encode(text).tolist()  # Convert to list for Weaviate

    def store_text_in_weaviate(self, text: str, embedding: list, pdf_name: str):
        document = {
            "content": text,
            "pdf_name": pdf_name
        }
        
        # Check if the collection exists
        if "PDFDocuments" not in self.client.collections.list_all():
            self.client.collections.create(
                name="PDFDocuments",
                vectorizer_config={"vectorIndexType": "hnsw"},  # Use HNSW indexing
                properties=[
                    {"name": "content", "dataType": "string"},
                    {"name": "pdf_name", "dataType": "string"}
                ]
            )

        self.client.collections.get("PDFDocuments").data.insert(
            properties=document,
            vector=embedding
        )
