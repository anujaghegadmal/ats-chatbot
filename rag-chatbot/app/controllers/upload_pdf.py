from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz  # PyMuPDF for extracting text & images
import nltk
from nltk.tokenize import word_tokenize
import weaviate
import shutil
import os
from PIL import Image
import io
import cv2
import numpy as np
from app.config import settings

app = FastAPI()

# Initialize Weaviate client
client = weaviate.Client(
    url=settings.weaviate_url,
    additional_headers={"X-OpenAI-Api-Key": settings.openai_api_key}
)

# Directory to store uploaded PDFs
UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text.strip()

# Function to extract images from a PDF
def extract_images_from_pdf(pdf_path: str):
    """Extract images from a PDF file."""
    doc = fitz.open(pdf_path)
    images = []
    for i, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_pil = Image.open(io.BytesIO(image_bytes))
            images.append(img_pil)
    return images

# Function to check for charts in images using OpenCV
def check_for_charts(image):
    """Detect charts in an image using OpenCV."""
    image_np = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect circles (Pie charts)
    circles = cv2.HoughCircles(
        edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30, param1=50, param2=30, minRadius=10, maxRadius=100
    )

    # Detect lines (Bar charts)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)

    return bool(circles) or bool(lines)

# Function to tokenize the extracted text
def tokenize_text(text: str) -> list[str]:
    nltk.download('punkt')  # Ensure tokenization resources are available
    return word_tokenize(text)

# Function to store tokenized text in Weaviate
def store_text_in_weaviate(text: str, tokens: list[str], pdf_name: str):
    document = {
        "content": text,
        "tokens": tokens,
        "pdf_name": pdf_name
    }
    client.data_object.create(class_name="PDFDocument", data=document)

@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Classify resumes and store data in Weaviate."""
    
    try:
        # Save the uploaded file temporarily
        file_location = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(file_location)
        has_text = bool(extracted_text)

        # Extract images from the PDF
        extracted_images = extract_images_from_pdf(file_location)
        has_images = len(extracted_images) > 0

        # Check for charts in the images
        has_charts = any(check_for_charts(img) for img in extracted_images)

        # Tokenize the extracted text
        tokens = tokenize_text(extracted_text)

        # Store the extracted text and tokens in Weaviate
        store_text_in_weaviate(extracted_text, tokens, file.filename)

        # Classify Resume Type
        if has_text and not has_images:
            resume_type = "Traditional Resume"
        elif has_images and not has_charts:
            resume_type = "Resume with Images"
        elif has_images and has_charts:
            resume_type = "Resume with Charts"
        else:
            resume_type = "Unknown Format"

        return {
            "resume_type": resume_type,
            "has_text": has_text,
            "has_images": has_images,
            "has_charts": has_charts,
            "message": "File uploaded, processed, and stored in Weaviate successfully."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
