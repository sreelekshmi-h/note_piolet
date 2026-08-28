from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from pydantic import BaseModel

import os
import shutil

from rag import (
    process_pdf,
    generate_answer
)


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

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )


    # --------------------------------
    # Create safe file name
    # --------------------------------

    filename = os.path.basename(
        file.filename
    )


    file_path = os.path.join(
        DATA_DIR,
        filename
    )


    # --------------------------------
    # Save uploaded PDF
    # --------------------------------

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # --------------------------------
    # Process PDF
    # --------------------------------

    try:

        chunks_added = process_pdf(
            file_path
        )

    except Exception as e:

        # Delete failed upload

        if os.path.exists(file_path):

            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )


    # --------------------------------
    # Check PDF content
    # --------------------------------

    if chunks_added == 0:

        return {
            "message": (
                "PDF uploaded, but no readable "
                "text was found."
            ),
            "filename": filename,
            "chunks_added": 0
        }


    return {
        "message": "PDF uploaded successfully",
        "filename": filename,
        "chunks_added": chunks_added
    }


# --------------------------------
# Ask question
# --------------------------------

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    # --------------------------------
    # Validate question
    # --------------------------------

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )


    # --------------------------------
    # Generate answer
    # --------------------------------

    try:

        result = generate_answer(
            request.question
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )


    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }
