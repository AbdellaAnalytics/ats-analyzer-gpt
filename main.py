from fastapi import FastAPI, UploadFile, File
import PyPDF2
import docx2txt
import tempfile
import openai
import os
from dotenv import load_dotenv

# تحميل المفتاح من .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = ""

    # استخراج النص من PDF
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        for page in reader.pages:
            content += page.extract_text()

    # استخراج النص من DOCX
    elif file.filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        content = docx2txt.process(tmp_path)

    else:
        return {"error": "Only PDF or DOCX files are allowed."}

    # تحليل المحتوى باستخدام GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert resume reviewer."},
            {"role": "user", "content": f"Analyze the following resume and give feedback:\n\n{content}"}
        ]
    )

    feedback = response['choices'][0]['message']['content']
    return {
        "summary": feedback
    }
