import os
import shutil
import fitz  # PyMuPDF for extracting text from PDFs
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException

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
        print("extracted_text", extracted_text)
        
        # Generating embeddings
        embedding = self.generate_embedding(extracted_text)
        # print("embedding", embedding)
        
        # Storing in Weaviate
        self.store_text_in_weaviate(extracted_text, embedding, file.filename)

        return {"message": "File uploaded and processed successfully."}

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text("text") for page in doc)

    def generate_embedding(self, text: str):
        """Generating embeddings using Sentence Transformers."""
        return embedding_model.encode(text).tolist()

    # def store_text_in_weaviate(self, text: str, embedding: list, pdf_name: str):
    #     document = {
    #         "content": text,
    #         "pdf_name": pdf_name
    #     }

    #     # Check if class exists in Weaviate
    #     schema = self.client.schema.get()
    #     existing_classes = [cls["class"] for cls in schema.get("classes", [])]

    #     if "PDFDocuments" not in existing_classes:
    #         pdf_class = {
    #             "class": "PDFDocuments",
    #             "vectorizer": "none",  # Disable built-in vectorizer since we provide embeddings
    #             "properties": [
    #                 {"name": "content", "dataType": ["text"]},
    #                 {"name": "pdf_name", "dataType": ["string"]}
    #             ]
    #         }
    #         self.client.schema.create_class(pdf_class)

    #     # Insert document
    #     self.client.data_object.create(
    #         data_object=document,
    #         class_name="PDFDocuments",
    #         vector=embedding
    #     )

    def store_text_in_weaviate(self, text: str, embedding: list, pdf_name: str):
        document = {
            "content": text,
            "pdf_name": pdf_name
        }

        # Check if class exists in Weaviate
        schema = self.client.schema.get()
        existing_classes = [cls["class"] for cls in schema.get("classes", [])]

        if "PDFDocuments" not in existing_classes:
            pdf_class = {
                "class": "PDFDocuments",
                "vectorizer": "none",  
                # "vectorizer": "text2vec-transformers",
                "properties": [
                    {"name": "content", "dataType": ["text"]},
                    {"name": "pdf_name", "dataType": ["string"]}
                ]
            }
            self.client.schema.create_class(pdf_class)

        response = self.client.data_object.create(
            data_object=document,
            class_name="PDFDocuments",
            vector=embedding   # remove this for automatic vectorization
        )

        if response:
            print("Success: Document stored in Weaviate.")
        else:
            print("Failure: Document was not stored in Weaviate.")


    def get_documents(self):
        query = """
        {
            Get {
                PDFDocuments {
                    content
                    pdf_name
                }
            }
        }
        """
        response = self.client.query.raw(query)
        
        if "errors" in response:
            raise HTTPException(status_code=500, detail=response["errors"])

        return {"documents": response["data"]["Get"]["PDFDocuments"]}
