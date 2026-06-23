from app.utils.llm_client import call_llm
from rag.prompt_builder import build_rag_prompt

def generate_idea(topic):
    base_prompt = f"""You are a creative book strategist.
Generate a compelling book idea for the topic: "{topic}".

Include:
- What the book is about
- Who it is for
- Why it matters
- The unique angle or perspective

Keep it concise, 1 paragraph.
"""
    prompt = build_rag_prompt(base_prompt, query=topic)
    return call_llm(prompt)
