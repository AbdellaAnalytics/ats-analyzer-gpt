from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import tempfile
import docx2txt
import PyPDF2
from dotenv import load_dotenv

# ✅ تحميل المتغيرات من .env
load_dotenv()

# ✅ إعداد FastAPI
app = FastAPI()

# ✅ إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ تحميل مفتاح API من environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ دالة لاستخراج النص من ملفات PDF و DOCX
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        return docx2txt.process(tmp_path)
    else:
        return "Unsupported file type"

# ✅ مسار الرفع
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    extracted_text = extract_text(file)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that reviews CVs and gives feedback."},
            {"role": "user", "content": extracted_text}
        ]
    )

    return {"feedback": response.choices[0].message.content}
