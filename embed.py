"""
embed.py — Milestone 4a: Embedding + Vector Store

Loads chunks from chunks.json, generates embeddings with all-MiniLM-L6-v2,
and stores them in a persistent ChromaDB collection with all metadata.

Usage:
    python embed.py              # build / rebuild the collection
    python embed.py --reset      # drop and rebuild from scratch
"""

import argparse
import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_FILE = "chunks.json"
CHROMA_DIR  = "chroma_db"
COLLECTION  = "sec_filings"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE  = 256   # embed this many chunks per call to avoid OOM on large corpora


def load_chunks(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def build_collection(chunks: list[dict], reset: bool = False) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    if reset and COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
        print(f"Dropped existing collection '{COLLECTION}'")

    collection = client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},   # cosine similarity as per planning.md
    )

    existing = collection.count()
    if existing > 0 and not reset:
        print(f"Collection already has {existing} documents — skipping embed. Use --reset to rebuild.")
        return collection

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    texts     = [c["text"]     for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # IDs must be unique strings; use a stable zero-padded global index
    ids = [f"chunk_{i:05d}" for i in range(len(chunks))]

    total = len(chunks)
    added = 0
    print(f"Embedding {total} chunks in batches of {BATCH_SIZE}...")

    for start in range(0, total, BATCH_SIZE):
        end        = min(start + BATCH_SIZE, total)
        batch_text = texts[start:end]
        batch_meta = metadatas[start:end]
        batch_ids  = ids[start:end]

        embeddings = model.encode(batch_text, show_progress_bar=False).tolist()

        collection.add(
            ids        = batch_ids,
            embeddings = embeddings,
            documents  = batch_text,
            metadatas  = batch_meta,
        )
        added += len(batch_text)
        pct = added / total * 100
        print(f"  [{added:>5}/{total}]  {pct:.1f}%", end="\r", flush=True)

    print(f"\nStored {added} chunks in ChromaDB at '{CHROMA_DIR}/'")
    return collection


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed chunks into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Drop and rebuild the collection")
    args = parser.parse_args()

    chunks_path = Path(CHUNKS_FILE)
    if not chunks_path.exists():
        print(f"ERROR: {CHUNKS_FILE} not found — run ingest.py first")
        sys.exit(1)

    chunks = load_chunks(CHUNKS_FILE)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    collection = build_collection(chunks, reset=args.reset)
    print(f"Collection '{COLLECTION}' ready — {collection.count()} documents indexed")


if __name__ == "__main__":
    main()
