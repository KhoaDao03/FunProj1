"""
retrieve.py — Milestone 4b: Retrieval

Embeds a plain-English query with all-MiniLM-L6-v2, runs cosine similarity
search against the ChromaDB collection, and returns the top-k chunks with
text and full source metadata.

Usage (CLI):
    python retrieve.py "What was NVIDIA's total revenue for fiscal year 2025?"
    python retrieve.py "What are Intel's primary competitive risks?" --top-k 5

Usage (as a module):
    from retrieve import retrieve
    results = retrieve("What was NVIDIA's revenue?")
    for r in results:
        print(r["metadata"]["ticker"], r["metadata"]["filing_year"], r["score"])
        print(r["text"][:300])
"""

import argparse
import re
import sys

from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_DIR  = "chroma_db"
COLLECTION  = "sec_filings"
EMBED_MODEL = "all-MiniLM-L6-v2"
DEFAULT_K   = 7

TICKER_TO_COMPANY = {
    "AAPL": "Apple Inc.",
    "AMZN": "Amazon.com, Inc.",
    "AVGO": "Broadcom Inc.",
    "GOOG": "Alphabet Inc.",
    "INTC": "Intel Corporation",
    "META": "Meta Platforms, Inc.",
    "MSFT": "Microsoft Corporation",
    "MU": "Micron Technology, Inc.",
    "NVDA": "NVIDIA Corporation",
    "SPCX": "Space Exploration Technologies Corp.",
    "TSLA": "Tesla, Inc.",
    "NFLX": "Netflix, Inc.",
}

COMPANY_ALIASES = {
    "AAPL": ["Apple", "Apple Inc."],
    "AMZN": ["Amazon", "Amazon.com", "Amazon.com, Inc."],
    "AVGO": ["Broadcom", "Broadcom Inc."],
    "GOOG": ["Alphabet", "Google", "Alphabet Inc."],
    "INTC": ["Intel", "Intel Corporation"],
    "META": ["Meta", "Meta Platforms", "Meta Platforms, Inc."],
    "MSFT": ["Microsoft", "Microsoft Corporation"],
    "MU": ["Micron", "Micron Technology", "Micron Technology, Inc."],
    "NVDA": ["NVIDIA", "Nvidia", "NVIDIA Corporation"],
    "SPCX": ["SpaceX", "Space Exploration Technologies", "Space Exploration Technologies Corp."],
    "TSLA": ["Tesla", "Tesla, Inc."],
    "NFLX": ["Netflix", "Netflix, Inc."],
}

# Module-level singletons — loaded once per process
_model:      SentenceTransformer | None = None
_collection: chromadb.Collection | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION)
    return _collection


def _infer_where(query: str) -> dict | None:
    """
    Derive a light metadata filter from the query text.

    This is intentionally conservative:
    - If the query names a single company, filter to that company.
    - If the query mentions a single filing year, filter to that year.
    - If both are present, combine them so the vector search cannot drift to
      another issuer or year with a similar topic.

    If the query mentions multiple years or no recognizable company, leave the
    search unfiltered so we do not overconstrain retrieval.
    """
    lowered = query.lower()

    matched_ticker = None
    alias_pairs = []
    for ticker, aliases in COMPANY_ALIASES.items():
        for alias in aliases:
            alias_pairs.append((ticker, alias))

    # Prefer longer aliases first so "Amazon.com" beats "Amazon", etc.
    for ticker, alias in sorted(alias_pairs, key=lambda kv: len(kv[1]), reverse=True):
        if re.search(rf"\b{re.escape(alias.lower())}\b", lowered):
            matched_ticker = ticker
            break

    years = sorted(set(re.findall(r"\b(2024|2025|2026)\b", query)))

    clauses = []
    if matched_ticker:
        clauses.append(("ticker", matched_ticker))
    if len(years) == 1:
        clauses.append(("filing_year", years[0]))

    if not clauses:
        return None
    if len(clauses) == 1:
        key, value = clauses[0]
        return {key: value}
    return {"$and": [{key: value} for key, value in clauses]}


def retrieve(query: str, top_k: int = DEFAULT_K) -> list[dict]:
    """
    Embed the query and return the top_k most similar chunks.

    Each result dict has:
        text      — chunk text
        metadata  — {ticker, company, filing_type, filing_year, section,
                     source_file, chunk_index, extraction_method}
        score     — cosine similarity (0–1; higher is more similar)
        id        — chunk ID in ChromaDB
    """
    model      = _get_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()
    where = _infer_where(query)

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where is not None:
        query_kwargs["where"] = where

    response = collection.query(**query_kwargs)

    results = []
    for doc, meta, dist in zip(
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        # ChromaDB cosine space returns distance = 1 - similarity
        similarity = 1.0 - dist
        results.append({
            "text":     doc,
            "metadata": meta,
            "score":    round(similarity, 4),
            "id":       response["ids"][0][len(results)],
        })

    return results


def _format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        m = r["metadata"]
        header = (
            f"[{i}] {m['ticker']} {m['filing_type']} {m['filing_year']}  "
            f"§ {m['section']}  "
            f"(score: {r['score']:.4f})"
        )
        lines.append(header)
        lines.append(r["text"][:500].replace("\n", " ").strip())
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve relevant chunks for a query")
    parser.add_argument("query", nargs="+", help="Natural language query")
    parser.add_argument("--top-k", type=int, default=DEFAULT_K, help=f"Number of results (default: {DEFAULT_K})")
    args = parser.parse_args()

    query = " ".join(args.query)
    print(f"Query : {query}")
    print(f"Top-k : {args.top_k}\n")

    try:
        results = retrieve(query, top_k=args.top_k)
    except Exception as e:
        print(f"ERROR: {e}")
        print("Hint: run embed.py first to build the ChromaDB collection.")
        sys.exit(1)

    if not results:
        print("No results returned.")
        sys.exit(0)

    print(_format_results(results))


if __name__ == "__main__":
    main()
