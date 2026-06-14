"""
ingest.py — Ingestion and chunking pipeline for SEC filings RAG system.

Three-layer text extraction per document:
  1. Native  — PyMuPDF direct text extraction (fast, works on text-based PDFs)
  2. URL     — fetch the SEC EDGAR HTML filing and parse it (handles image-based PDFs)
  3. OCR     — Tesseract on rendered page images at 200 DPI (last resort)

Cleans boilerplate, splits by SEC Item section headings, and chunks each section
with overlap. Writes all chunks with metadata to chunks.json.

Usage:
    python ingest.py                  # all three layers
    python ingest.py --no-ocr         # native + URL only (no Tesseract)
"""

import json
import re
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ~700 tokens × 4 chars/token ≈ 2800 chars; overlap ~125 tokens × 4 = 500 chars
CHUNK_SIZE = 2800
CHUNK_OVERLAP = 500

# OCR render resolution
OCR_DPI = 200

# SEC EDGAR requires a descriptive User-Agent or it blocks requests
SEC_HEADERS = {
    "User-Agent": "StudentResearchProject research@example.com",
    "Accept-Encoding": "gzip, deflate",
}

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

# Map each PDF filename to its original SEC EDGAR HTML URL
FILENAME_TO_URL = {
    "AAPL-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm",
    "AMZN-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm",
    "AVGO-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm",
    "GOOG-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm",
    "INTC-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/50863/000005086326000011/intc-20251227.htm",
    "META-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm",
    "MSFT-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm",
    "MU-K10-2025.pdf":   "https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/mu-20250828.htm",
    "NVDA-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm",
    "SPCX-S1-2026.pdf":  "https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm",
    "TSLA-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm",
    "NFLX-K10-2025.pdf": "https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm",
    "AAPL-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm",
    "AMZN-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm",
    "AVGO-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1730168/000173016824000139/avgo-20241103.htm",
    "GOOG-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm",
    "INTC-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/50863/000005086325000009/intc-20241228.htm",
    "META-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm",
    "MSFT-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/789019/000095017024087843/msft-20240630.htm",
    "MU-K10-2024.pdf":   "https://www.sec.gov/Archives/edgar/data/723125/000072312524000027/mu-20240829.htm",
    "NVDA-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/nvda-20240128.htm",
    "TSLA-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm",
    "NFLX-K10-2024.pdf": "https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm",
}

# Matches "ITEM 1A. Risk Factors", "Item 7. MD&A", "ITEM 15 — Exhibits", etc.
ITEM_HEADING_RE = re.compile(
    r"(?m)^\s*(?:ITEM|Item)\s+(\d{1,2}[A-C]?)[\s.\-–—]+(.+)\s*$"
)

BOILERPLATE_PATTERNS = [
    # Table-of-contents lines: "Item 1A. Risk Factors ......... 12"
    re.compile(r"(?m)^.{0,100}\.{3,}\s*\d{1,4}\s*$"),
    # "TABLE OF CONTENTS" header
    re.compile(r"(?mi)^\s*table\s+of\s+contents\s*$"),
    # Standalone page numbers
    re.compile(r"(?m)^\s*\d{1,4}\s*$"),
    # Financial statement page labels: "F-1", "F-12"
    re.compile(r"(?m)^\s*F-\d+\s*$"),
    # "Page X of Y" footers
    re.compile(r"(?mi)^\s*page\s+\d+\s+of\s+\d+\s*$"),
    # "(continued)" markers
    re.compile(r"(?mi)^\s*\(continued\)\s*$"),
    # Horizontal rules
    re.compile(r"(?m)^\s*[-_]{4,}\s*$"),
]

FORWARD_LOOKING_RE = re.compile(
    r"(?is)(?:^|\n)(?:CAUTIONARY|SPECIAL\s+NOTE).{0,50}?FORWARD.LOOKING"
    r".+?(?=\n\n(?:[A-Z]|\Z))",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Filename parsing
# ---------------------------------------------------------------------------

def parse_filename(filename: str) -> dict:
    """Extract ticker, company, filing_type, and filing_year from filename."""
    stem = Path(filename).stem
    parts = stem.split("-")
    ticker = parts[0]

    raw_type = parts[1].upper() if len(parts) > 1 else ""
    if raw_type == "K10":
        filing_type = "10-K"
    elif raw_type == "S1":
        filing_type = "S-1"
    else:
        filing_type = raw_type

    return {
        "ticker": ticker,
        "company": TICKER_TO_COMPANY.get(ticker, ticker),
        "filing_type": filing_type,
        "filing_year": parts[2] if len(parts) > 2 else "unknown",
    }


# ---------------------------------------------------------------------------
# Layer 1: Native PDF text extraction
# ---------------------------------------------------------------------------

def _extract_native(pdf: fitz.Document) -> str:
    """Direct PyMuPDF text extraction. Returns empty string if no text found."""
    pages = [
        page.get_text("text").strip()
        for page in pdf
        if page.get_text("text").strip()
    ]
    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# Layer 2: SEC EDGAR URL extraction
# ---------------------------------------------------------------------------

def _extract_url(url: str) -> str:
    """
    Fetch the SEC EDGAR HTML filing and extract clean text via BeautifulSoup.

    SEC EDGAR filings use iXBRL (inline XBRL) format: the <ix:header> block
    at the top contains machine-readable financial metadata that must be stripped
    before get_text() — otherwise XBRL codes pollute the output. The rest of
    the body contains the actual human-readable filing text.
    """
    resp = requests.get(url, headers=SEC_HEADERS, timeout=60)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    # Strip non-content tags; ix:header is the iXBRL metadata block
    for tag in soup(["script", "style", "head", "nav", "footer", "header", "ix:header"]):
        tag.decompose()

    body = soup.find("body") or soup
    text = body.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Layer 3: OCR fallback
# ---------------------------------------------------------------------------

def _extract_ocr(pdf: fitz.Document, label: str) -> str:
    """
    Render each page to a 200-DPI image and run Tesseract OCR.
    Prints a live page counter that overwrites itself on the same line.
    """
    import pytesseract
    from PIL import Image

    scale = OCR_DPI / 72
    mat = fitz.Matrix(scale, scale)
    total = len(pdf)
    pages = []

    for i, page in enumerate(pdf):
        sys.stdout.write(f"\r  {label:<30} OCR page {i + 1}/{total}...")
        sys.stdout.flush()
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, config="--psm 6")
        if text.strip():
            pages.append(text.strip())

    # Return cursor to column 0 so caller can overwrite with the result line
    sys.stdout.write(f"\r  {label:<30} ")
    sys.stdout.flush()

    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# Extraction orchestrator
# ---------------------------------------------------------------------------

def extract_text(pdf_path: Path, use_ocr: bool = True) -> tuple[str, str]:
    """
    Returns (text, method) where method is one of: 'native', 'url', 'ocr'.

    Priority:
      1. Native PDF text extraction (fast, zero network)
      2. SEC EDGAR HTML URL (clean text, requires network)
      3. Tesseract OCR on rendered page images (slow, no network needed)
    """
    # --- Layer 1: native ---
    try:
        with fitz.open(pdf_path) as pdf:
            if len(pdf) > 0:
                text = _extract_native(pdf)
                if text.strip():
                    return text, "native"
    except Exception:
        pass  # corrupt/empty file — fall through

    # --- Layer 2: URL ---
    url = FILENAME_TO_URL.get(pdf_path.name)
    if url:
        try:
            sys.stdout.write("(trying URL) ")
            sys.stdout.flush()
            text = _extract_url(url)
            if text.strip():
                return text, "url"
        except Exception as e:
            sys.stdout.write(f"(URL failed: {e}) ")
            sys.stdout.flush()

    # --- Layer 3: OCR ---
    if not use_ocr:
        raise ValueError(
            "No extractable text found and OCR is disabled (pass --no-ocr to skip)."
        )

    try:
        with fitz.open(pdf_path) as pdf:
            if len(pdf) == 0:
                raise ValueError("PDF has no pages.")
            text = _extract_ocr(pdf, pdf_path.name)
            if not text.strip():
                raise ValueError("OCR produced no text.")
            return text, "ocr"
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"All three extraction layers failed: {e}")


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove boilerplate that would pollute embeddings."""
    text = FORWARD_LOOKING_RE.sub("", text)
    for pattern in BOILERPLATE_PATTERNS:
        text = pattern.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

def split_into_sections(text: str) -> list[tuple[str, str]]:
    """
    Split document text into (section_title, section_text) pairs using
    SEC Item heading patterns. Falls back to ("Document", full_text) if
    no Item headings are detected.
    """
    matches = list(ITEM_HEADING_RE.finditer(text))

    if not matches:
        return [("Document", text)]

    sections = []

    preamble = text[: matches[0].start()].strip()
    if len(preamble) > 300:
        sections.append(("Cover / Preamble", preamble))

    for i, match in enumerate(matches):
        item_num = match.group(1)
        item_title = match.group(2).strip().rstrip(".")
        section_title = f"Item {item_num} — {item_title}"
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        if len(section_text) > 150:
            sections.append((section_title, section_text))

    return sections if sections else [("Document", text)]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_document(
    pdf_path: Path,
    splitter: RecursiveCharacterTextSplitter,
    use_ocr: bool = True,
) -> tuple[list[dict], str]:
    """
    Full pipeline for a single PDF:
      extract → clean → section split → chunk → attach metadata

    Returns (chunks, extraction_method).
    """
    meta = parse_filename(pdf_path.name)
    raw_text, method = extract_text(pdf_path, use_ocr=use_ocr)
    cleaned = clean_text(raw_text)
    sections = split_into_sections(cleaned)

    chunks = []
    for section_title, section_text in sections:
        for i, piece in enumerate(splitter.split_text(section_text)):
            piece = piece.strip()
            if len(piece) < 100:
                continue
            chunks.append({
                "text": piece,
                "metadata": {
                    **meta,
                    "section": section_title,
                    "source_file": str(pdf_path),
                    "chunk_index": i,
                    "extraction_method": method,
                },
            })
    return chunks, method


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    use_ocr = "--no-ocr" not in sys.argv

    documents_dir = Path("documents")
    output_path = Path("chunks.json")

    if not documents_dir.exists():
        print(f"ERROR: '{documents_dir}' directory not found.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    pdf_files = sorted(documents_dir.glob("*.pdf"))

    layers = "native → URL → OCR" if use_ocr else "native → URL only"
    print(f"Found {len(pdf_files)} PDF files  [{layers}]\n")

    all_chunks = []
    method_counts = {"native": 0, "url": 0, "ocr": 0}
    failed_docs = []
    t_start = time.time()

    for pdf_path in pdf_files:
        sys.stdout.write(f"  {pdf_path.name:<30} ")
        sys.stdout.flush()
        t0 = time.time()

        try:
            chunks, method = chunk_document(pdf_path, splitter, use_ocr=use_ocr)
            elapsed = time.time() - t0
            print(f"{len(chunks):>5} chunks  [{method:<6}]  {elapsed:.0f}s")
            all_chunks.extend(chunks)
            method_counts[method] += 1
        except Exception as e:
            elapsed = time.time() - t0
            print(f"FAILED — {e}  {elapsed:.0f}s")
            failed_docs.append(pdf_path.name)

    output_path.write_text(json.dumps(all_chunks, indent=2))

    wall = time.time() - t_start
    print(f"\n{'─' * 55}")
    print(f"  Documents    : {len(pdf_files) - len(failed_docs)}/{len(pdf_files)} processed")
    print(f"  Native       : {method_counts['native']}")
    print(f"  URL          : {method_counts['url']}")
    print(f"  OCR          : {method_counts['ocr']}")
    if failed_docs:
        print(f"  Failed       : {len(failed_docs)}")
        for name in failed_docs:
            print(f"                 {name}")
    print(f"  Total chunks : {len(all_chunks)}")
    print(f"  Output       : {output_path}")
    print(f"  Wall time    : {wall:.0f}s")
    print(f"{'─' * 55}")

    # Verification samples
    if all_chunks:
        print("\n--- Sample chunk (first) ---")
        s = all_chunks[0]
        print(f"  Company  : {s['metadata']['company']} ({s['metadata']['filing_year']})")
        print(f"  Section  : {s['metadata']['section']}")
        print(f"  Method   : {s['metadata']['extraction_method']}")
        print(f"  Chars    : {len(s['text'])}")
        print(f"  Preview  : {s['text'][:200].replace(chr(10), ' ')}...")

    if len(all_chunks) > 1:
        print("\n--- Sample chunk (middle) ---")
        s = all_chunks[len(all_chunks) // 2]
        print(f"  Company  : {s['metadata']['company']} ({s['metadata']['filing_year']})")
        print(f"  Section  : {s['metadata']['section']}")
        print(f"  Method   : {s['metadata']['extraction_method']}")
        print(f"  Chars    : {len(s['text'])}")
        print(f"  Preview  : {s['text'][:200].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    main()
