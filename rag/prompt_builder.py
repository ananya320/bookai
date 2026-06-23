from rag.rag_engine import retrieve_context, format_context_for_prompt

def build_rag_prompt(base_prompt: str, query: str, use_rag: bool = True, top_k: int = 5):
    if not use_rag:
        return base_prompt

    chunks = retrieve_context(query, top_k=top_k)
    if not chunks:
        return base_prompt

    context_block = format_context_for_prompt(chunks)

    return f"""{base_prompt}

{context_block}

Use the reference material above to ground your response with accurate details.
If the references are not relevant, ignore them and use your general knowledge.
"""

def build_planner_prompt(topic: str, genre: str, target_audience: str):
    query = f"{topic} {genre} book structure"
    base = f"""You are an expert book planner. Create a detailed chapter outline for a {genre} book
about "{topic}" aimed at {target_audience}.

For each chapter provide:
- Chapter number and title
- Key themes and concepts to cover
- Estimated word count
- How this chapter connects to the overall narrative arc

Topic: {topic}
Genre: {genre}
Target Audience: {target_audience}
"""
    return build_rag_prompt(base, query)

def build_writer_prompt(chapter_title: str, chapter_summary: str, book_topic: str, genre: str, previous_chapter_summary: str = ""):
    query = f"{book_topic} {chapter_title} {chapter_summary}"

    continuity = ""
    if previous_chapter_summary:
        continuity = f"\nPrevious chapter summary: {previous_chapter_summary}\nMaintain continuity with the above.\n"

    base = f"""You are a professional author writing a {genre} book about "{book_topic}".

Write a full, engaging chapter based on the plan below.
{continuity}
Chapter Title: {chapter_title}
Chapter Plan: {chapter_summary}

Guidelines:
- Write in a compelling, {genre}-appropriate style
- Include specific facts, examples, and details
- Aim for 600-1000 words
- End with a smooth transition to the next chapter
"""
    return build_rag_prompt(base, query)

def build_memory_summary_prompt(chapter_text: str, existing_memory: str):
    return f"""You are a book memory manager. Summarize the key facts, characters,
and plot points from the chapter below. Merge with existing memory to avoid duplication.

Existing Memory:
{existing_memory or "No memory yet."}

New Chapter:
{chapter_text}

Return a concise, structured memory update in bullet points.
"""

def build_qa_prompt(question: str, book_topic: str):
    query = f"{question} {book_topic}"
    chunks = retrieve_context(query, top_k=6)
    context_block = format_context_for_prompt(chunks)

    if not chunks:
        return f"""Answer the following question about "{book_topic}" using your general knowledge.

Question: {question}
"""

    return f"""You are a knowledgeable assistant. Answer the question below using ONLY
the reference material provided. If the answer is not in the references, say so clearly.

{context_block}

Question: {question}

Provide a clear, concise answer with source references.
"""