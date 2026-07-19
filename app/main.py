from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
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


# ---------------------------------------------------------------------
# New: JSON API used by the redesigned /ui page (character name, storyline,
# genre form + bookshelf archive). These are separate from the routes above
# so nothing existing breaks.
# ---------------------------------------------------------------------

class GenerateRequest(BaseModel):
    character_name: str = ""
    storyline: str
    genre: str = "Fantasy"
    length: str = "medium"


@app.post("/generate")
def generate_story(req: GenerateRequest):
    combined_topic = req.storyline
    if req.genre:
        combined_topic += f" (Genre: {req.genre})"
    if req.character_name:
        combined_topic += f" (Main character: {req.character_name})"

    try:
        result = run_pipeline(
            combined_topic,
            character_name=req.character_name,
            genre=req.genre,
            storyline=req.storyline
        )
        return {
            "id": result["id"],
            "title": result["title"],
            "story": result["content"]
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/archive")
def archive_list():
    try:
        stories = get_all_stories()
    except Exception as e:
        return {"error": str(e)}

    return [
        {
            "id": s.get("id"),
            "title": s.get("title", "Untitled"),
            "genre": s.get("genre", ""),
            "character_name": s.get("character_name", ""),
            "created_at": s.get("created_at", "")
        }
        for s in stories if s.get("id")
    ]


@app.get("/archive/{story_id}")
def archive_item(story_id: str):
    try:
        stories = get_all_stories()
    except Exception as e:
        return {"error": str(e)}

    for s in stories:
        if s.get("id") == story_id:
            return {
                "id": s["id"],
                "title": s.get("title", "Untitled"),
                "genre": s.get("genre", ""),
                "character_name": s.get("character_name", ""),
                "created_at": s.get("created_at", ""),
                "story": s.get("content", "")
            }

    return {"error": "Story not found"}
