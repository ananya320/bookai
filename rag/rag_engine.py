import os
import hashlib
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = "bookai_knowledge"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K_RESULTS = 5

def _get_chroma_client():
    return chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False),
    )

def _get_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

def _get_embeddings():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

def load_document(file_path: str):
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in (".txt", ".md"):
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    raw_docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    return [
        {
            "text": chunk.page_content,
            "metadata": {**chunk.metadata, "source": path.name},
        }
        for chunk in chunks
    ]

def ingest_document(file_path: str):
    chunks = load_document(file_path)
    if not chunks:
        return {"status": "empty", "chunks_added": 0}

    embeddings_model = _get_embeddings()
    client = _get_chroma_client()
    collection = _get_collection(client)

    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [hashlib.md5(t.encode()).hexdigest() for t in texts]
    vectors = embeddings_model.embed_documents(texts)

    existing = set(collection.get(ids=ids)["ids"])
    new_items = [
        (i, v, m, t)
        for i, v, m, t in zip(ids, vectors, metadatas, texts)
        if i not in existing
    ]

    if new_items:
        n_ids, n_vecs, n_metas, n_texts = zip(*new_items)
        collection.add(
            ids=list(n_ids),
            embeddings=list(n_vecs),
            metadatas=list(n_metas),
            documents=list(n_texts),
        )

    return {
        "status": "success",
        "file": Path(file_path).name,
        "total_chunks": len(chunks),
        "chunks_added": len(new_items),
        "chunks_skipped": len(chunks) - len(new_items),
    }

def retrieve_context(query: str, top_k: int = TOP_K_RESULTS):
    embeddings_model = _get_embeddings()
    client = _get_chroma_client()
    collection = _get_collection(client)

    if collection.count() == 0:
        return []

    query_vector = embeddings_model.embed_query(query)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", None),
            "score": round(1 - dist, 4),
        })

    return output

def format_context_for_prompt(chunks):
    if not chunks:
        return ""

    lines = ["=== Retrieved Reference Material ==="]
    for i, chunk in enumerate(chunks, 1):
        source_label = f"[{chunk['source']}"
        if chunk.get("page") is not None:
            source_label += f", p.{chunk['page'] + 1}"
        source_label += "]"
        lines.append(f"\n[{i}] {source_label}\n{chunk['text']}")
    lines.append("\n=== End of Reference Material ===")
    return "\n".join(lines)

def list_indexed_sources():
    client = _get_chroma_client()
    collection = _get_collection(client)
    if collection.count() == 0:
        return []
    all_meta = collection.get(include=["metadatas"])["metadatas"]
    return sorted(set(m.get("source", "unknown") for m in all_meta))

def delete_source(filename: str):
    client = _get_chroma_client()
    collection = _get_collection(client)
    results = collection.get(where={"source": filename}, include=["metadatas"])
    ids_to_delete = results["ids"]
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    return {"deleted_chunks": len(ids_to_delete), "source": filename}

def clear_all():
    client = _get_chroma_client()
    client.delete_collection(COLLECTION_NAME)
    return {"status": "cleared"}