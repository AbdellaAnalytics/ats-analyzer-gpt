import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import PyPDF2
import docx2txt
import openai

# تحميل متغيرات البيئة
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# إعداد FastAPI
app = FastAPI()

# إعدادات CORS (مهم لو هتربط بواجهة خارجية زي React أو HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# دالة استخراج النص من ملف PDF أو DOCX
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif file.filename.endswith(".docx"):
        return docx2txt.process(file.file)
    else:
        return "Unsupported file format."

# دالة المعالجة الذكية للنص بالذكاء الاصطناعي
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text(file)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "أنت مساعد خبير في تحليل السير الذاتية."},
            {"role": "user", "content": f"قيم السيرة الذاتية التالية من حيث التنسيق، الكلمات المفتاحية، ومدى توافقها مع نظام ATS:\n\n{text}"}
        ]
    )

    return {"analysis": response.choices[0].message.content}
