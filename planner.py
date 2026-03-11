from app.utils.llm_client import call_llm


def create_outline(idea):

    prompt = f"""
    Create a book outline with chapters for this idea:

    {idea}

    Include 4 chapters with short descriptions.
    """

    response = call_llm(prompt)

    return response
