from app.utils.llm_client import call_llm
from rag.prompt_builder import build_rag_prompt

def write_content(outline):
    base_prompt = f"""You are a professional author.
Write a full book based on this chapter outline:

{outline}

For each chapter:
- Write 2-3 detailed paragraphs
- Use clear, engaging language
- Include examples and explanations

Write all chapters in full.
"""
    prompt = build_rag_prompt(base_prompt, query=outline)
    return call_llm(prompt)