import os
from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
import openai
import docx2txt
import PyPDF2
import tempfile

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.filename.endswith(".docx"):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        temp.write(file.file.read())
        temp.close()
        return docx2txt.process(temp.name)
    else:
        return "Unsupported file format"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text(file)
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Analyze this resume:\n{text}"}
        ]
    )

    return {"result": response.choices[0].message.content}
