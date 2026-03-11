from app.agents.ideator import generate_idea
from app.agents.planner import create_outline
from app.agents.writer import write_content
from app.agents.copy_editor import edit_content
from app.agents.summarizer import summarize
from app.utils.memory_manager import save_story


def run_pipeline(topic):

    # Step 1: Generate idea
    idea = generate_idea(topic)

    # Step 2: Create outline
    outline = create_outline(idea)

    # Step 3: Write content
    content = write_content(outline)

    # Step 4: Edit content
    edited = edit_content(content)

    # Step 5: Generate summary
    summary = summarize(edited)

    # Final result
    result = {
        "topic": topic,
        "idea": idea,
        "outline": outline,
        "content": edited,
        "summary": summary
    }

    # Save to memory JSON
    save_story(result)

    return result
    
