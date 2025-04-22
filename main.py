from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from dotenv import load_dotenv
import docx2txt
import PyPDF2
import tempfile

# ✅ Load env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ FastAPI app
app = FastAPI()

# ✅ CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Extract text
def extract_text_from_file(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file.filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file.file.read())
            temp_path = temp_file.name
        return docx2txt.process(temp_path)
    return ""

# ✅ Upload endpoint
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text_from_file(file)
    if not text:
        return {"error": "No text extracted"}

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an ATS resume analyzer."},
            {"role": "user", "content": f"Analyze this resume:\n{text}"}
        ]
    )

    return {"result": response.choices[0].message.content}
