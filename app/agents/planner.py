from app.utils.llm_client import call_llm
from rag.prompt_builder import build_rag_prompt

def create_outline(idea):
    base_prompt = f"""You are an expert book planner.
Based on this book idea, create a detailed chapter outline:

{idea}

For each chapter provide:
- Chapter number and title
- 2-3 sentences on what it covers

Give 5-6 chapters total.
"""
    prompt = build_rag_prompt(base_prompt, query=idea)
    return call_llm(prompt)