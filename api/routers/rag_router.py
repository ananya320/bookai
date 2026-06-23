import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from rag.rag_engine import clear_all, delete_source, ingest_document, list_indexed_sources, retrieve_context
from rag.prompt_builder import build_qa_prompt

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QARequest(BaseModel):
    question: str
    book_topic: str = ""

class DeleteRequest(BaseModel):
    filename: str

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = ingest_document(tmp_path)
        result["file"] = file.filename
    finally:
        os.unlink(tmp_path)

    return result

@router.post("/retrieve")
async def retrieve(req: QueryRequest):
    chunks = retrieve_context(req.query, top_k=req.top_k)
    return {"query": req.query, "results": chunks, "count": len(chunks)}

@router.post("/ask")
async def ask(req: QARequest):
    from openai import OpenAI
    prompt = build_qa_prompt(req.question, req.book_topic)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return {"question": req.question, "answer": response.choices[0].message.content}

@router.get("/sources")
async def list_sources():
    sources = list_indexed_sources()
    return {"sources": sources, "count": len(sources)}

@router.delete("/source")
async def delete_document(req: DeleteRequest):
    result = delete_source(req.filename)
    if result["deleted_chunks"] == 0:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{req.filename}'")
    return result

@router.delete("/all")
async def clear_knowledge_base():
    return clear_all()