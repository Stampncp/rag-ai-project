import os
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="AI RAG API Service with Gemini")

class QueryRequest(BaseModel):
    question: str

@app.post("/api/chat")
async def chat_with_gemini(request: QueryRequest):
    if not os.getenv("GEMINI_API_KEY"):
        return {"answer": "❌ ยังไม่ได้ตั้งค่า GEMINI_API_KEY ในระบบ API Service ครับ"}

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(request.question)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": f"❌ เกิดข้อผิดพลาดจาก Gemini API: {str(e)}"}
