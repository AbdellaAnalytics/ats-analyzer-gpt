from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import docx2txt
import PyPDF2
import tempfile

# تحميل متغيرات البيئة
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# إعداد التطبيق
app = FastAPI()

# تفعيل CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# استخراج النص من PDF أو DOCX
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    elif file.filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        return docx2txt.process(tmp_path)
    else:
        return "Unsupported file type"

# مسار الرفع
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text(file)
    
    if not text.strip():
        return {"error": "No extractable text found in file."}

    # استدعاء GPT لتحليل النص
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that checks resumes."},
            {"role": "user", "content": f"Analyze this resume and give me feedback:\n{text}"}
        ]
    )
    
    return {"feedback": response.choices[0].message.content}
