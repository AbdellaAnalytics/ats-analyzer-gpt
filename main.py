from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
import docx2txt
import tempfile

# ✅ تحميل متغيرات البيئة
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ إعداد FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ استخراج النص من ملف PDF
def extract_text_from_pdf(file_path):
    with fitz.open(file_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    return text

# ✅ استخراج النص من ملف DOCX
def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

# ✅ تحليل الملف المرفوع
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(tmp_path)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(tmp_path)
    else:
        return {"error": "Unsupported file type. Please upload a PDF or DOCX."}

    # ✅ طلب لتحليل النص باستخدام GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert ATS resume checker."},
            {"role": "user", "content": f"Analyze this resume:\n{text}"}
        ]
    )

    return {"result": response.choices[0].message.content}
