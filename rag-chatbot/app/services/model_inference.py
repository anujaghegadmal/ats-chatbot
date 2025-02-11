import os
import cohere
from typing import Dict, List
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from app.services.weaviate import connect_to_weaviate

# Load environment variables
load_dotenv()

# Initialize Cohere Client and Embedding Model
co = cohere.Client(api_key=os.environ.get("COHERE_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

async def query_profiles(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Queries Weaviate for similar profiles based on the given query."""
    print("Entering query_profiles")
    client = await connect_to_weaviate()
    query_embedding = embedding_model.encode(query)
    
    response = client.query.get("PDFDocuments", ["pdf_name", "content", "emp_id"])
    response = response.with_near_vector({"vector": query_embedding}).with_limit(limit).do()
    
    if response and "data" in response and response["data"].get("Get", {}).get("PDFDocuments"):
        print("Query results retrieved successfully")
        return response["data"]["Get"]["PDFDocuments"]
    
    return []

HR_ASSISTANT_PROMPT = """
You are an HR assistant specialized in resume analysis and HR analytics. Your primary focus is streamlining HR processes by providing insights about employee profiles and resumes.

Core Guidelines:
1. Be creative and thoughtful while maintaining accuracy.
2. Use professional but simple language, avoiding corporate jargon.
3. Structure responses in an easily digestible format.
4. Maintain strict confidentiality of all resume data.
5. Only answer questions related to resumes and profiles.
6. Always include profile_name and employee_id in responses.
7. Ensure filenames correspond to employee_id.

Response Format:
- Total Resumes Found: Clearly state the count of unique profiles at the beginning.
- Summary: Brief overview of analyzed profiles.
- Detailed Analysis: Bullet points for each profile.
- Recommendations (if applicable).

Error Handling:
- Non-resume queries: "I can only assist with resume-related questions."
- Incomplete data: Indicate missing information.
- Ambiguous queries: Request clarification.

Privacy Guidelines:
- Never share sensitive personal information.
- Aggregate data where possible.
- Flag potential privacy concerns.
"""

async def generate_detailed_response(query: str, profiles: List[Dict[str, str]]) -> dict:
    """Generates a detailed response using Cohere's API based on retrieved profiles."""
    print("Processing generate_detailed_response")
    
    # Construct a summary of profiles
    profiles_summary = [
        {"emp_id": profile["emp_id"], "pdf_name": profile["pdf_name"], "content": profile["content"]}
        for profile in profiles
    ]
    
    # Construct the prompt for Cohere API
    prompt_text = f"Query: {query}\n\nProfiles: {profiles_summary}"
    print("Generated Prompt =>", prompt_text)
    
    # Call Cohere API
    response = co.chat(
        message=prompt_text,
        model="command-r",
        # temperature=0.7,
        max_tokens=4000
    )
    
    print("Cohere API Response =>", response.text)
    return response.text