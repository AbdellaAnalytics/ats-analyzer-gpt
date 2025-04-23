from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from dotenv import load_dotenv
import docx2txt
import PyPDF2
import tempfile
import aiofiles
import aiofiles.os as aios
from typing import Optional
import io

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def extract_text_from_file(file: UploadFile) -> Optional[str]:
    try:
        if file.filename.endswith(".pdf"):
            pdf_content = await file.read()
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif file.filename.endswith(".docx"):
            temp_path = None
            try:
                async with aiofiles.tempfile.NamedTemporaryFile("wb", suffix=".docx", delete=False) as tmp:
                    temp_path = tmp.name
                    await tmp.write(await file.read())
                return docx2txt.process(temp_path)
            finally:
                if temp_path and await aios.path.exists(temp_path):
                    await aios.remove(temp_path)
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, detail="Only PDF and DOCX files are supported")

    content = await extract_text_from_file(file)
    if not content:
        raise HTTPException(400, detail="Could not extract text or file is empty")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد توظيف متخصص في تحليل السير الذاتية بناءً على معايير ATS."},
                {"role": "user", "content": content}
            ]
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(500, detail=f"Error from OpenAI: {str(e)}")
