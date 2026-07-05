import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="AI RAG API Service with Gemini")

# คลังเก็บความรู้จำลองในหน่วยความจำ
KNOWLEDGE_STORE = []

# ดึงค่า API Key จาก Kubernetes Secret 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class QueryRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    content: str

# 1. Endpoint สำหรับคุยและดึงความรู้ RAG
@app.post("/api/chat")
async def chat_with_gemini(request: QueryRequest):
    if not GEMINI_API_KEY:
        return {"answer": "Error: Gemini API Key missing"}
    
    context = ""
    if KNOWLEDGE_STORE:
        context = "\n".join(KNOWLEDGE_STORE)
        prompt = f"คุณเป็นผู้ช่วยผู้เชี่ยวชาญ จงใช้บริบทต่อไปนี้ตอบคำถาม:\n{context}\n\nคำถาม: {request.question}"
    else:
        prompt = request.question

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": f"เกิดข้อผิดพลาด: {str(e)}"}

# 2. Endpoint สำหรับเพิ่มข้อความดิบเข้าคลัง RAG
@app.post("/api/ingest", summary="ใส่ข้อมูลหรือข้อความดิบเข้าคลังความรู้")
async def ingest_data(request: IngestRequest):
    if not request.content.strip():
        return {"status": "error", "message": "กรุณาใส่ข้อความก่อนส่ง"}
    KNOWLEDGE_STORE.append(request.content)
    return {"status": "success", "message": "บันทึกข้อความเข้าคลัง RAG เรียบร้อยแล้ว!"}

# 3. Endpoint สำหรับอัปโหลดข้อความ (ใช้ Raw Request ป้องกันปัญหาคอนเทนเนอร์ขาด Library)
@app.post("/api/upload", summary="อัปโหลดข้อความหรือไฟล์ Raw Text เข้าคลัง RAG")
async def upload_file(request: Request):
    try:
        body = await request.body()
        text_content = body.decode("utf-8")
        if not text_content.strip():
            return {"status": "error", "message": "ไม่พบเนื้อหาข้อความ"}
        KNOWLEDGE_STORE.append(text_content)
        return {"status": "success", "message": "นำเข้าข้อมูลเข้าคลัง RAG สำเร็จ!"}
    except Exception as e:
        return {"status": "error", "message": f"เกิดข้อผิดพลาด: {str(e)}"}