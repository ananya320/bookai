import uuid
from datetime import datetime, timezone

from app.agents.ideator import generate_idea
from app.agents.planner import create_outline
from app.agents.writer import write_content
from app.agents.copy_editor import edit_content
from app.agents.summarizer import summarize
from app.utils.memory_manager import save_story


def run_pipeline(topic, character_name="", genre="", storyline=""):

    idea = generate_idea(topic)
    outline = create_outline(idea)
    content = write_content(outline)
    edited = edit_content(content)
    summary = summarize(edited)

    if character_name and genre:
        title = f"{character_name}'s {genre} Story"
    elif genre:
        title = f"A {genre} Story"
    else:
        title = (storyline or topic)[:60]

    result = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "character_name": character_name,
        "genre": genre,
        "storyline": storyline,
        "topic": topic,
        "idea": idea,
        "outline": outline,
        "content": edited,
        "summary": summary
    }

    save_story(result)
    return result
    
    
