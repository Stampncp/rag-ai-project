import os  # 🟢 ห้ามลบ! จำเป็นต้องใช้ดึง API Key
from fastapi import FastAPI, UploadFile, File  # 🟢 รวมกลุ่มอิมพอร์ต FastAPI ไว้ด้วยกัน
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="AI RAG API Service with Gemini")

# 1. สร้างกล่องความรู้จำลอง (In-Memory Database) ไว้เก็บข้อความที่อัปโหลดเข้ามา
KNOWLEDGE_STORE = []

# ดึงค่า API Key จาก Kubernetes Secret
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class QueryRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    content: str

# --- Endpoint 1: สำหรับคุย (Chat) และดึงข้อมูลบริบทจากคลังมาอ้างอิง ---
@app.post("/api/chat")
async def chat_with_gemini(request: QueryRequest):
    if not GEMINI_API_KEY:
        return {"answer": "Error: Gemini API Key missing ในระบบคลาวด์"}
    
    # 🔍 ส่วนดึงบริบท (RAG Retrieval)
    context = ""
    if KNOWLEDGE_STORE:
        context = "\n".join(KNOWLEDGE_STORE)
        prompt = f"คุณเป็นผู้ช่วยผู้เชี่ยวชาญ จงใช้ข้อมูลบริบทต่อไปนี้เพื่อตอบคำถาม:\n{context}\n\nคำถาม: {request.question}"
    else:
        prompt = request.question

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": f"เกิดข้อผิดพลาดในการเรียก AI: {str(e)}"}

# --- Endpoint 2: สำหรับเพิ่มข้อความดิบเข้าคลัง ---
@app.post("/api/ingest", summary="ใส่ข้อมูลหรือข้อความดิบเข้าคลังความรู้")
async def ingest_data(request: IngestRequest):
    if not request.content.strip():
        return {"status": "error", "message": "กรุณาใส่ข้อความก่อนส่ง"}
    KNOWLEDGE_STORE.append(request.content)
    return {"status": "success", "message": "บันทึกข้อความเข้าคลัง RAG เรียบร้อยแล้ว!"}

# --- Endpoint 3: สำหรับอัปโหลดไฟล์ข้อความ ---
@app.post("/api/upload", summary="อัปโหลดไฟล์ข้อความ (.txt) เข้าระบบ")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        return {"status": "error", "message": "ระบบรองรับเฉพาะไฟล์นามสกุล .txt เท่านั้น"}
    try:
        body = await file.read()
        text_content = body.decode("utf-8")
        KNOWLEDGE_STORE.append(text_content)
        return {"status": "success", "filename": file.filename, "message": "สับย่อยไฟล์เข้าคลัง RAG สำเร็จ!"}
    except Exception as e:
        return {"status": "error", "message": f"เกิดข้อผิดพลาด: {str(e)}"}