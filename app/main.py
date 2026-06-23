from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.orchestrator import run_pipeline
from app.utils.memory_manager import get_all_stories
from api.routers.rag_router import router as rag_router

app = FastAPI(title="BookAI", version="1.0")

app.include_router(rag_router, prefix="/rag", tags=["RAG"])

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home():
    return {"message": "Book AI system running"}


@app.get("/generate-book")
def generate_book(topic: str):
    try:
        result = run_pipeline(topic)
        return result
    except Exception as e:
        return {"error": str(e)}


@app.get("/stories")
def get_stories():
    try:
        return get_all_stories()
    except Exception as e:
        return {"error": str(e)}


@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/generate-book-ui", response_class=HTMLResponse)
def generate_book_ui(request: Request, topic: str = Form(...)):
    try:
        result = run_pipeline(topic)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"result": result}
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(e)}
        )