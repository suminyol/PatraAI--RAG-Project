from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import shutil
import os
import re

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from langchain_pinecone import PineconeVectorStore

# Environment

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN is missing from .env")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing from .env")

# LangChain's Pinecone wrapper automatically looks for this exact environment variable
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


# =========================
# FastAPI
# =========================

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Hugging Face
# =========================

client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)


# =========================
# Embeddings
# =========================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================
# PineconeDB
# =========================

index_name = "patra-ai" 

vectorstore = PineconeVectorStore(
    index_name=index_name,
    embedding=embedding_model
)

# =========================
# Retriever
# =========================

# =========================
# Retriever
# =========================

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 15,          # CHANGE: Increased from 4 to 15 chunks
        "fetch_k": 50,    # CHANGE: Increased from 10 to 50 for better diversity
        "lambda_mult": 0.5
    }
)


# =========================
# Prompt
# =========================

# =========================
# Prompt
# =========================

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a highly capable and intelligent AI assistant.

            Below is context retrieved from the user's uploaded documents. Use this context as your primary foundation to answer the question. 
            
            However, you are NOT limited to this context. If the document does not contain the complete answer, or if you can provide a better, more comprehensive response by bringing in your own general knowledge and reasoning, you should do so. 
            
            When appropriate, seamlessly blend the document's facts with your own out-of-the-box thinking.
            """
        ),
        (
            "human",
            """
            Context:
            {context}

            Question:
            {question}
            """
        )
    ]
)


# =========================
# Request Model
# =========================

class ChatRequest(BaseModel):
    query: str


# =========================
# Upload PDF
# =========================

# =========================
# Upload PDFs (Multiple)
# =========================

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...)
):
    os.makedirs("temp_uploads", exist_ok=True)
    
    processed_files = []
    failed_files = []
    total_chunks = 0

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            failed_files.append(f"{file.filename} (Not a PDF)")
            continue

        temp_file_path = os.path.join("temp_uploads", file.filename)

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            # Load PDF
            loader = PyPDFLoader(temp_file_path)
            docs = loader.load()

            # Split documents
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_documents(docs)

            if chunks:
                vectorstore.add_documents(chunks)
                total_chunks += len(chunks)
                processed_files.append(file.filename)
            else:
                failed_files.append(f"{file.filename} (No text extracted)")

        except Exception as e:
            failed_files.append(f"{file.filename} (Error: {str(e)})")

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return {
        "message": f"Upload complete. Processed {len(processed_files)} files.",
        "processed": processed_files,
        "failed": failed_files,
        "total_chunks_added": total_chunks
    }

# =========================
# Chat
# =========================

@app.post("/chat")
async def chat(request: ChatRequest):

    try:

        # -------------------------
        # Retrieve relevant chunks
        # -------------------------

        docs = retriever.invoke(
            request.query
        )

        if not docs:
            return {
                "answer": "I could not find the answer in the document.",
                "sources": []
            }

        # -------------------------
        # Build context
        # -------------------------

        context = "\n\n".join(
            doc.page_content
            for doc in docs
            if doc.page_content.strip()
        )

        # -------------------------
        # Create prompt
        # -------------------------

        final_prompt = prompt_template.invoke(
            {
                "context": context,
                "question": request.query
            }
        )

        # Convert LangChain messages
        # into Hugging Face messages

        messages = [
            {
                "role": message.type,
                "content": message.content
            }
            for message in final_prompt.messages
        ]

        # LangChain uses "human"
        # Hugging Face expects "user"

        for message in messages:

            if message["role"] == "human":
                message["role"] = "user"

            elif message["role"] == "ai":
                message["role"] = "assistant"


        # -------------------------
        # Hugging Face Chat
        # -------------------------

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:fastest",
            messages=messages,
            max_tokens=4096 # NEW: Increased from 512 to 4096 so the answer doesn't cut off
        )

        raw_answer = response.choices[0].message.content

        # NEW: Remove <think>...</think> and all content inside it
        clean_answer = re.sub(r'<think>.*?</think>', '', raw_answer, flags=re.DOTALL).strip()


        # -------------------------
        # Return response
        # -------------------------

        return {
            "answer": clean_answer, # NEW: Returning the cleaned answer
            "sources": [
                {
                    "content": doc.page_content[:150] + "..."
                }
                for doc in docs
            ]
        }


    except Exception as e:

        print("CHAT ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )