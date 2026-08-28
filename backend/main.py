from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

import os
import shutil

from rag import process_pdf, generate_answer


# --------------------------------
# Create FastAPI application
# --------------------------------

app = FastAPI(
    title="AI Notes Assistant",
    description="RAG-based study assistant",
    version="1.0"
)


# --------------------------------
# Data directory
# --------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# --------------------------------
# Question model
# --------------------------------

class QuestionRequest(BaseModel):

    question: str


# --------------------------------
# Home endpoint
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "AI Notes Assistant API is running"
    }


# --------------------------------
# Upload PDF
# --------------------------------

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # Check file type

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )


    # Create file path

    file_path = os.path.join(
        DATA_DIR,
        file.filename
    )


    # Save uploaded PDF

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # Process PDF

    chunks_added = process_pdf(
        file_path
    )


    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "chunks_added": chunks_added
    }


# --------------------------------
# Ask question
# --------------------------------

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    result = generate_answer(
        request.question
    )


    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }
