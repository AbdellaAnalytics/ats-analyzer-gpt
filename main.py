from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from dotenv import load_dotenv
import docx2txt
import PyPDF2
import tempfile

# تحميل متغيرات البيئة
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# إنشاء التطبيق
app = FastAPI()

# السماح بالوصول من جميع المواقع (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# استخراج النص من ملفات PDF و DOCX
def extract_text_from_file(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.file.read())
            return docx2txt.process(tmp.name)
    return ""

# تحليل السيرة الذاتية باستخدام GPT
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = extract_text_from_file(file)
    if not content:
        return {"error": "الملف لا يحتوي على نص يمكن تحليله."}

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "أنت مساعد توظيف متخصص في تحليل السير الذاتية بناءً على معايير ATS."},
            {"role": "user", "content": content}
        ]
    )
    return {"result": response.choices[0].message.content}
