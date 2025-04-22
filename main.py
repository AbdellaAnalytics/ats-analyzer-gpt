from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import docx2txt
import PyPDF2
import tempfile
import os
from dotenv import load_dotenv

# ✅ تحميل متغيرات البيئة
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ تهيئة OpenAI client
client = OpenAI(api_key=api_key)

# ✅ إنشاء تطبيق FastAPI
app = FastAPI()

# ✅ إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ استخراج النص من ملف PDF أو DOCX
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif file.filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        text = docx2txt.process(tmp_path)
        os.remove(tmp_path)
        return text
    else:
        return "Unsupported file type"

# ✅ المسار الأساسي
@app.get("/")
def read_root():
    return {"message": "ATS Analyzer API is running."}

# ✅ مسار الرفع والتحليل
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text(file)

    # ✅ استدعاء OpenAI لتحليل النص
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert resume analyst."},
            {"role": "user", "content": f"Analyze this resume:\n{text}"}
        ]
    )

    analysis = response.choices[0].message.content
    return {"analysis": analysis}
