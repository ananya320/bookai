import os
import tempfile
import pytest

os.environ["CHROMA_DB_PATH"] = tempfile.mkdtemp()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")

from rag.rag_engine import clear_all, delete_source, format_context_for_prompt, list_indexed_sources, load_document
from rag.prompt_builder import build_planner_prompt, build_writer_prompt, build_qa_prompt

def test_load_txt_document(tmp_path):
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Python is a programming language.\n" * 100)
    chunks = load_document(str(txt_file))
    assert len(chunks) > 0
    assert chunks[0]["metadata"]["source"] == "sample.txt"

def test_unsupported_file_type(tmp_path):
    bad_file = tmp_path / "data.csv"
    bad_file.write_text("col1,col2\n1,2")
    with pytest.raises(ValueError):
        load_document(str(bad_file))

def test_format_context_empty():
    assert format_context_for_prompt([]) == ""

def test_planner_prompt(tmp_path):
    prompt = build_planner_prompt("Machine Learning", "non-fiction", "beginners")
    assert "Machine Learning" in prompt

def test_writer_prompt(tmp_path):
    prompt = build_writer_prompt("Chapter 1", "Intro to AI", "AI", "technical")
    assert "Chapter 1" in prompt

def test_list_sources_empty():
    clear_all()
    assert list_indexed_sources() == []

def test_delete_nonexistent():
    result = delete_source("fake.pdf")
    assert result["deleted_chunks"] == 0