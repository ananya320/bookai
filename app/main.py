from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.orchestrator import run_pipeline
from app.utils.memory_manager import get_all_stories

# ── ADD THIS LINE ──
from api.routers.rag_router import router as rag_router

app = FastAPI(title="BookAI", version="1.0")

# ── ADD THIS LINE ──
app.include_router(rag_router, prefix="/rag", tags=["RAG"])

# Templates directory
templates = Jinja2Templates(directory="templates")


# ✅ Health check
@app.get("/")
def home():
    return {"message": "Book AI system running"}


# ✅ API: Generate book (GET)
@app.get("/generate-book")
def generate_book(topic: str):
    try:
        result = run_pipeline(topic)
        return result
    except Exception as e:
        return {"error": str(e)}


# ✅ API: Get all saved stories
@app.get("/stories")
def get_stories():
    try:
        return get_all_stories()
    except Exception as e:
        return {"error": str(e)}


# ✅ UI Page
@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ✅ UI Form Handler (POST)
@app.post("/generate-book-ui", response_class=HTMLResponse)
def generate_book_ui(request: Request, topic: str = Form(...)):
    try:
        result = run_pipeline(topic)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": result
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(e)
            }
        )