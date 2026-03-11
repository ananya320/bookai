from app.utils.llm_client import call_llm

def edit_content(content):
    prompt = f"Edit and improve this content: {content}"
    return call_llm(prompt)
