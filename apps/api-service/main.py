from fastapi import UploadFile, File
from pydantic import BaseModel

# 1. สร้างกล่องความรู้จำลอง (In-Memory Database) ไว้เก็บข้อความที่อัปโหลดเข้ามา
KNOWLEDGE_STORE = []

# สร้างโครงสร้างสำหรับรับข้อความผ่านไอคอน Ingest
class IngestRequest(BaseModel):
    content: str

# 2. เพิ่มปุ่ม POST /api/ingest สำหรับพิมพ์ส่งข้อความสดเข้าระบบ
@app.post("/api/ingest", summary="ใส่ข้อมูลหรือข้อความดิบเข้าคลังความรู้")
async def ingest_data(request: IngestRequest):
    if not request.content.strip():
        return {"status": "error", "message": "กรุณาใส่ข้อความดียก่อนส่ง"}
    KNOWLEDGE_STORE.append(request.content)
    return {"status": "success", "message": "บันทึกข้อความเข้าฐานข้อมูลเวกเตอร์จำลองเรียบร้อยแล้ว!"}

# 3. เพิ่มปุ่ม POST /api/upload สำหรับเลือกไฟล์อัปโหลดจากเครื่อง
@app.post("/api/upload", summary="อัปโหลดไฟล์ข้อความ (.txt) เข้าระบบ")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        return {"status": "error", "message": "ระบบรองรับเฉพาะไฟล์นามสกุล .txt เท่านั้นในปัจจุบัน"}
    try:
        body = await file.read()
        text_content = body.decode("utf-8")
        KNOWLEDGE_STORE.append(text_content)
        return {"status": "success", "filename": file.filename, "message": "อัปโหลดและสับย่อยไฟล์เข้าคลัง RAG สำเร็จ!"}
    except Exception as e:
        return {"status": "error", "message": f"เกิดข้อผิดพลาด: {str(e)}"}