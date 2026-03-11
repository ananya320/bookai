from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.orchestrator import run_pipeline
from app.utils.memory_manager import get_all_stories

app = FastAPI()

# Jinja2 templates directory
templates = Jinja2Templates(directory="templates")


# Health check
@app.get("/")
def home():
    return {"message": "Book AI system running"}


# API: Generate book
@app.get("/generate-book")
def generate_book(topic: str):
    try:
        result = run_pipeline(topic)
        return result
    except Exception as e:
        return {"error": str(e)}


# API: Get all saved stories
@app.get("/stories")
def get_stories():
    try:
        return get_all_stories()
    except Exception as e:
        return {"error": str(e)}


# UI: Render HTML interface
@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
