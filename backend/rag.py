import os
from pathlib import Path
import pymupdf as fitz
from embeddings import create_embeddings,create_embedding
from vectorstore import add_documents,search_documents,get_collection_count
from dotenv import load_dotenv
from groq import Groq


# Get the directory containing rag.py
BASE_DIR = Path(__file__).resolve().parent

# Load .env from backend/
ENV_FILE = BASE_DIR / ".env"

print("Looking for .env at:", ENV_FILE)
print(".env exists:", ENV_FILE.exists())

load_dotenv(ENV_FILE)

print("GROQ API KEY LOADED:", bool(os.getenv("GROQ_API_KEY")))


# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)




# --------------------------------
# Extract PDF text
# --------------------------------

def extract_pdf_pages(pdf_path):

    pdf = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(pdf):

        text = page.get_text()

        if text.strip():

            pages.append({
                "text": text,
                "page": page_number + 1
            })

    pdf.close()

    return pages


# --------------------------------
# Create chunks
# --------------------------------

def chunk_text(
    text,
    chunk_size=500,
    chunk_overlap=50
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += chunk_size - chunk_overlap

    return chunks


# --------------------------------
# Process PDF
# --------------------------------

def process_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    pages = extract_pdf_pages(pdf_path)

    all_chunks = []
    ids = []
    metadatas = []

    for page in pages:

        chunks = chunk_text(
            page["text"]
        )

        for chunk_number, chunk in enumerate(chunks):

            all_chunks.append(chunk)

            ids.append(
                f"{filename}_{page['page']}_{chunk_number}"
            )

            metadatas.append({
                "source": filename,
                "page": page["page"],
                "chunk": chunk_number
            })

    # Create embeddings

    embeddings = create_embeddings(
        all_chunks
    )

    # Store in ChromaDB

    add_documents(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    return len(all_chunks)


# --------------------------------
# Retrieve relevant documents
# --------------------------------

def retrieve_documents(
    question,
    n_results=5
):

    # Convert question into embedding

    query_embedding = create_embedding(
        question
    )

    # Search ChromaDB

    results = search_documents(
        query_embedding,
        n_results
    )

    return results


# --------------------------------
# Generate answer using Groq
# --------------------------------

def generate_answer(
    question,
    n_results=5
):

    # Retrieve relevant chunks

    results = retrieve_documents(
        question,
        n_results
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]


    # Combine retrieved chunks

    context_parts = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        context_parts.append(
            f"""
Source: {metadata["source"]}
Page: {metadata["page"]}

{document}
"""
        )

    context = "\n\n".join(
        context_parts
    )


    # Prompt for the LLM

    prompt =prompt = f"""
You are an AI Notes Assistant and personal study partner.

Your job is to help students study using ONLY the information
retrieved from their uploaded lecture notes.

The student can upload lecture notes as PDF files and ask you to:

1. Explain concepts in simple language
2. Generate multiple-choice questions (MCQs)
3. Summarize chapters or modules
4. Help prepare for exams
5. Answer questions based on the uploaded notes
6. Clarify difficult topics with examples when the examples
   are supported by the provided notes

IMPORTANT RULES:

- Use ONLY the retrieved context from the student's notes.
- Do not use outside knowledge to answer.
- Do not invent facts that are not present in the notes.
- If the answer cannot be found in the provided context, say:
  "I don't know based on the provided notes."
- Keep explanations clear and student-friendly.
- For exam preparation, focus on important concepts, definitions,
  differences, steps, advantages, disadvantages, and key points
  present in the notes.
- When generating MCQs, create questions ONLY from the provided
  notes.
- For MCQs, provide four options (A, B, C, D), followed by the
  correct answer and a short explanation.
- When asked to summarize a chapter or module, organize the
  summary using headings and bullet points.
- If the user asks for a simple explanation, avoid unnecessarily
  complicated terminology.
- If the question refers to a specific chapter or module, use
  information from that chapter/module when it is available in
  the retrieved context.

Examples of tasks you should support:

Example 1:
User: "Explain deadlock in simple words"

Response style:
Explain the concept clearly and simply using the student's notes.

Example 2:
User: "Give me 5 MCQs from Chapter 3"

Response style:
Generate 5 MCQs based only on Chapter 3.
Each question should have:
A. ...
B. ...
C. ...
D. ...

Answer: B
Explanation: ...

Example 3:
User: "Summarize the networking module"

Response style:
Provide a concise, well-organized summary of the networking
module using headings and bullet points.

Example 4:
User: "Help me prepare for the exam from this chapter"

Response style:
Create an exam-focused study guide containing:
- Important concepts
- Important definitions
- Key points
- Important differences
- Potential exam questions
- Quick revision points

Do not claim that something is in the notes unless it appears
in the provided context.

-------------------------
RETRIEVED NOTES
-------------------------

{context}

-------------------------
STUDENT'S QUESTION
-------------------------

{question}

-------------------------
ANSWER
-------------------------
"""


    # Call Groq

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": "You are a helpful study assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )


    answer = response.choices[0].message.content


    # Return answer + sources

    sources = []

    for metadata in metadatas:

        sources.append({
            "source": metadata["source"],
            "page": metadata["page"]
        })


    return {
        "answer": answer,
        "sources": sources
    }