from app.utils.llm_client import call_llm


def write_content(outline):

    prompt = f"""
    Write a short book based on this outline.

    The book should have chapters.

    Outline:
    {outline}

    Write:
    Chapter 1
    Chapter 2
    Chapter 3
    """

    response = call_llm(prompt)

    return response
