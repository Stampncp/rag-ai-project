import streamlit as st
import requests
import os

st.set_page_config(page_title="AI RAG Chatbot", page_icon="🤖")
st.title("🤖 AI RAG Enterprise Chatbot")
st.caption("Microservice Architecture powered by Streamlit & FastAPI")

API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000/api/chat")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีครับ! ผมคือ AI RAG Chatbot ยินดีช่วยเหลือครับ มีอะไรให้ผมช่วยค้นหาไหมครับ?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("กำลังค้นหาคำตอบจากฐานข้อมูล..."):
            try:
                response = requests.post(API_URL, json={"question": prompt}, timeout=30)
                if response.status_code == 200:
                    answer = response.json().get("answer", "ไม่มีข้อมูลคำตอบจากระบบ")
                else:
                    answer = f"เกิดข้อผิดพลาดจาก API Service (Status: {response.status_code})"
            except requests.exceptions.RequestException:
                answer = "❌ ไม่สามารถเชื่อมต่อกับ API Service ได้ (กรุณาตรวจสอบว่าเปิดรัน FastAPI บน port 8000 หรือยัง)"
            
            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
