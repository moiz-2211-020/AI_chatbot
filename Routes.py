from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db
from model import ChatHistory
from fastapi import Depends
from dotenv import load_dotenv
import os


load_dotenv()
# Configuration
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
TOP_K = 3
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize services
qdrant = QdrantClient(host="qdrant_local", port=6333)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('models/gemini-1.5-flash')

app = FastAPI()

# Request body schema
class QueryRequest(BaseModel):
    question: str
#You are a helpful assistant answering based on a scientific document.You are a helpful assistant answering based on a scientific document.
# Helper to generate Gemini answer


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with actual frontend domain/IP for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_answer(context: str, query: str) -> str:
    prompt = f"""
You are a technical assistant. Respond to all questions with direct, concise, and factual answers. Do not use phrases like "Based on the provided text" or "According to the passage." Just give the answer in a clear, declarative sentence.
 
Context:
{context}

Question:
{query}

Answer:
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# Route for querying and answering

# Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@app.post("/ask")
async def ask_question(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        query_embedding = embedding_model.encode(request.question).tolist()

        search_result = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=TOP_K,
            with_payload=["text"],
            with_vectors=False

        )
        print(f"Number of results returned from Qdrant: {len(search_result)}")

        if not search_result:
            raise HTTPException(status_code=404, detail="No relevant context found.")

        context_chunks = "\n\n".join([hit.payload["text"] for hit in search_result if "text" in hit.payload])
       

        answer = generate_answer(context_chunks, request.question)

        # Save to chat history
        chat = ChatHistory(
            user_id=current_user["id"],
            question=request.question,
            answer=answer
        )
        db.add(chat)
        await db.commit()
        print("Chat save to db")

        return {"question": request.question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
