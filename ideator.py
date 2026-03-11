from app.utils.llm_client import call_llm

def generate_idea(topic):
    prompt = f"Generate a book idea about {topic}"
    return call_llm(prompt)
