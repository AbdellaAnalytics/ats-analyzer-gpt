from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
import docx2txt
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from PDF or DOCX
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        text = ""
        with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif file.filename.endswith(".docx"):
        with open("temp.docx", "wb") as f:
            f.write(file.file.read())
        return docx2txt.process("temp.docx")
    else:
        return ""

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text(file)
    if not text:
        return {"error": "Unsupported file type or empty content"}

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an ATS Resume Analyzer."},
            {"role": "user", "content": f"Analyze this resume and give me feedback:\n{text}"}
        ]
    )

    return {"analysis": response.choices[0].message.content}
