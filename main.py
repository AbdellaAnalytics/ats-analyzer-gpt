from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
import os
import fitz  # PyMuPDF
import docx2txt

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_file(file: UploadFile) -> str:
    if file.filename.endswith(".pdf"):
        with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
            return " ".join([page.get_text() for page in doc])
    elif file.filename.endswith(".docx"):
        return docx2txt.process(file.file)
    else:
        return file.file.read().decode("utf-8")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        text = extract_text_from_file(file)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that evaluates resumes."},
                {"role": "user", "content": f"Evaluate this resume and give feedback: {text}"}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return {"feedback": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
