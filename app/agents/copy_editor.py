from app.utils.llm_client import call_llm

def edit_content(content):
    prompt = f"""You are a professional copy editor.
Improve this book content for clarity, grammar, and flow.
Do not change the meaning, just improve the writing quality.

Content:
{content}
"""
    return call_llm(prompt)
