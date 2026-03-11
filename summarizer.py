from app.utils.llm_client import call_llm

def summarize(content):
    prompt = f"Summarize this book: {content}"
    return call_llm(prompt)