# Project 1: SEC Filings RAG System

---

## Domain

This system covers SEC company filing documents — specifically Form 10-K annual reports and Form S-1 registration statements from twelve major public companies (and one pre-IPO company). The knowledge in these documents is valuable because 10-K and S-1 filings are the most comprehensive, legally binding descriptions a company publishes about its business model, risks, revenue breakdown, competitive position, legal proceedings, and future outlook.

The problem is that these documents are extremely long — a single 10-K can run 100–200 pages — written in dense legal and financial language, and structured across dozens of numbered Items. A student, investor, or analyst trying to answer a single question like "What are this company's biggest manufacturing risks?" may need to scan dozens of pages manually. This system makes those documents searchable using plain-English questions.

The corpus covers 12 companies (Apple, Amazon, Broadcom, Alphabet/Google, Intel, Meta, Microsoft, Micron, NVIDIA, SpaceX, Tesla, Netflix) across two fiscal years (2024 and 2025), totaling 23 documents: 22 × Form 10-K and 1 × Form S-1 (SpaceX, the only pre-IPO company in the set).

---

## Document Sources

| # | Source | Type | File path | Original SEC URL |
|---|--------|------|-----------|------------------|
| 1 | Apple Inc. Annual Report | SEC Form 10-K | `documents/AAPL-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm |
| 2 | Amazon.com, Inc. Annual Report | SEC Form 10-K | `documents/AMZN-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm |
| 3 | Broadcom Inc. Annual Report | SEC Form 10-K | `documents/AVGO-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm |
| 4 | Alphabet Inc. Annual Report | SEC Form 10-K | `documents/GOOG-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm |
| 5 | Intel Corporation Annual Report | SEC Form 10-K | `documents/INTC-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/50863/000005086326000011/intc-20251227.htm |
| 6 | Meta Platforms, Inc. Annual Report | SEC Form 10-K | `documents/META-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm |
| 7 | Microsoft Corporation Annual Report | SEC Form 10-K | `documents/MSFT-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm |
| 8 | Micron Technology, Inc. Annual Report | SEC Form 10-K | `documents/MU-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/mu-20250828.htm |
| 9 | NVIDIA Corporation Annual Report | SEC Form 10-K | `documents/NVDA-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm |
| 10 | Space Exploration Technologies Corp. Registration Statement | SEC Form S-1 | `documents/SPCX-S1-2026.pdf` | https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm |
| 11 | Tesla, Inc. Annual Report | SEC Form 10-K | `documents/TSLA-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm |
| 12 | Netflix, Inc. Annual Report | SEC Form 10-K | `documents/NFLX-K10-2025.pdf` | https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm |
| 13 | Apple Inc. Annual Report | SEC Form 10-K | `documents/AAPL-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm |
| 14 | Amazon.com, Inc. Annual Report | SEC Form 10-K | `documents/AMZN-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm |
| 15 | Broadcom Inc. Annual Report | SEC Form 10-K | `documents/AVGO-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1730168/000173016824000139/avgo-20241103.htm |
| 16 | Alphabet Inc. Annual Report | SEC Form 10-K | `documents/GOOG-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm |
| 17 | Intel Corporation Annual Report | SEC Form 10-K | `documents/INTC-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/50863/000005086325000009/intc-20241228.htm |
| 18 | Meta Platforms, Inc. Annual Report | SEC Form 10-K | `documents/META-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm |
| 19 | Microsoft Corporation Annual Report | SEC Form 10-K | `documents/MSFT-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/789019/000095017024087843/msft-20240630.htm |
| 20 | Micron Technology, Inc. Annual Report | SEC Form 10-K | `documents/MU-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/723125/000072312524000027/mu-20240829.htm |
| 21 | NVIDIA Corporation Annual Report | SEC Form 10-K | `documents/NVDA-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/nvda-20240128.htm |
| 22 | Tesla, Inc. Annual Report | SEC Form 10-K | `documents/TSLA-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm |
| 23 | Netflix, Inc. Annual Report | SEC Form 10-K | `documents/NFLX-K10-2024.pdf` | https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm |

All documents are sourced directly from the SEC EDGAR public filing database.

---

## Chunking Strategy

**Chunk size:** 2,800 characters (~700 tokens) with a 500-character (~125 token) overlap. SEC filings are much longer than typical web documents and often express a single idea (a risk factor, a revenue explanation, a legal proceeding) across multiple dense paragraphs. A chunk under ~500 tokens frequently captures only one paragraph and loses the surrounding context needed to understand financial figures. 2,800 characters gives the retrieval model enough text to understand what a number refers to without exceeding the embedding model's effective input range.

**Overlap:** 500 characters (~125 tokens) between adjacent chunks. Financial ideas in SEC filings often continue across paragraph boundaries — a risk factor may name the risk in one paragraph and explain the dollar impact two paragraphs later. Without overlap, a chunk boundary would cut that connection and the retriever would return half the context. The overlap ensures key ideas are fully represented in at least one chunk.

**Tradeoffs this strategy creates:**
- Larger chunks make retrieval less precise: a chunk containing both a risk and a revenue paragraph may be retrieved for either type of question but is only half-relevant to each.
- The 500-character overlap means adjacent chunks share significant content, which increases the total stored data but reduces the chance of splitting a key idea at a boundary.
- At 2,800 characters, chunks exceed the 256-token input limit of `all-MiniLM-L6-v2`. This means the embedding model only encodes the first ~256 tokens (~1,000 characters) of each chunk during both indexing and retrieval. A longer-context embedding model would use the full chunk.

**Preprocessing before chunking:**
- Text was extracted using a three-layer pipeline: (1) native PyMuPDF text extraction, (2) SEC EDGAR HTML fetch + BeautifulSoup for documents whose PDFs were rendered as vector graphics, (3) Tesseract OCR as a last resort. 7 of 23 documents used native extraction; 16 used the URL layer; 0 required OCR.
- iXBRL metadata blocks (`<ix:header>`) were stripped before text extraction. Without this step, SEC EDGAR HTML files leak thousands of machine-readable XBRL taxonomy codes (`http://fasb.org/us-gaap/...`) into the text.
- Boilerplate was removed using regex patterns: table-of-contents dot leaders, standalone page numbers, `F-nn` financial page labels, repeated "Table of Contents" lines, horizontal rules, and forward-looking-statement disclaimer blocks.
- Text was split first by SEC Item headings (e.g., `Item 1A`, `Item 7`) to preserve section boundaries, then each section was further split by `RecursiveCharacterTextSplitter`.

**Final chunk count:** 5,112 chunks across 23 documents (wall time: 68 seconds).

---

## Sample Chunks

These five chunks are representative examples taken directly from `chunks.json`. They show the kind of content the retriever searches over.

### Sample Chunk 1
**Source:** `documents/NVDA-K10-2025.pdf` — Item 1 (Business)

```text
Our customers include all major public and private cloud providers, AI model makers,
enterprises and startups, and public sector entities. We work with industry leaders
to help build or transform their applications and data center infrastructure. Some of
our direct customers include Microsoft, Google, Amazon Web Services, Meta, Tesla,
and others. We focus on improving all aspects of computing — from algorithms and
software frameworks to chip architecture and memory — to accelerate AI and scientific
computing workloads.
```

### Sample Chunk 2
**Source:** `documents/AAPL-K10-2025.pdf` — Item 7 (MD&A)

```text
iPhone net sales increased during 2025 compared to 2024. The year-over-year growth
was driven by higher sales of iPhone 16 models. iPhone net sales:
  2025: $209,586 million
  2024: $201,183 million
  2023: $200,583 million
Services net sales increased during 2025 compared to 2024, driven by increases across
all Services categories.
  2025: $109,158 million
  2024: $96,169 million
```

### Sample Chunk 3
**Source:** `documents/TSLA-K10-2024.pdf` — Item 1A (Risk Factors)

```text
If we are unable to attract, hire and retain key employees and qualified personnel,
our ability to compete may be harmed. The loss of the services of any of our key
employees or any significant portion of our workforce could disrupt our operations
or delay the development, introduction and ramp of our products or services. We
depend on the services of our executive officers and other key personnel, including
those with highly specialized knowledge of electric vehicles, engineering, and
electrical and building construction expertise.
```

### Sample Chunk 4
**Source:** `documents/SPCX-S1-2026.pdf` — Cover / Preamble

```text
Founded in 2002, SpaceX is the only company building the integrated hardware and
software infrastructure of the future across space, connectivity, and AI. At our
core, we are builders. We design, manufacture, launch, and operate products and
services built on cutting-edge technologies, including the world's most advanced
rockets and spacecraft. We safely and reliably transport astronauts, satellites,
and other payloads on missions that benefit life on Earth. Since 2023, we have
launched more than 80% of mass to orbit for the world each year with an over 99%
mission success rate.
```

### Sample Chunk 5
**Source:** `documents/AMZN-K10-2025.pdf` — Item 7 (MD&A)

```text
Operating income by segment is as follows (in millions):
                    Year Ended December 31,
                          2024        2025
North America         $ 24,967    $ 29,619
International           3,792       4,750
AWS                    39,834      45,606
Consolidated         $ 68,593    $ 79,975

Operating income was $68.6 billion and $80.0 billion for 2024 and 2025.
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` from `sentence-transformers`. This model runs entirely locally — no API key, no per-query cost, no network dependency after the initial download. It has 22M parameters and produces 384-dimensional embeddings. For a prototype over 23 documents and 5,112 chunks, the full embedding pass completes in under two minutes on CPU.

**Why this model for this project:** It is fast, free, and well-suited for a development prototype. The `sentence-transformers` library wraps the model with a clean Python API (`SentenceTransformer("all-MiniLM-L6-v2")`), making it easy to integrate with ChromaDB.

**Production tradeoff reflection:**

- **Context length limit:** `all-MiniLM-L6-v2` has a hard 256-token input limit. Our chunks are ~700 tokens, so each chunk is silently truncated to roughly the first 1,000 characters during embedding. A longer-context model (e.g., `text-embedding-3-large` with an 8,191-token limit) would represent the full chunk, potentially improving retrieval for chunks where the most relevant content appears in the second half.

- **Domain-specific accuracy:** This is a general-purpose model trained on diverse web text. SEC filings use specialized terminology — *material weakness*, *going concern*, *operating lease liabilities*, *revenue recognition*, *non-GAAP measures*. A model fine-tuned on legal or financial text (e.g., a FinBERT-derived embedding model) would represent these terms more precisely, and would likely retrieve more relevant chunks for technical domain-specific queries.

- **Latency vs. accuracy tradeoff:** Larger embedding models produce higher-quality embeddings but add per-query latency. `all-MiniLM-L6-v2` is fast because it is small. For a real user-facing product, this tradeoff must be measured empirically — a 100ms vs 400ms retrieval step has a noticeable effect on perceived responsiveness.

- **Cost at scale:** Local models have zero per-query cost. API-based embedding models charge per token for both ingestion (one-time) and every query (ongoing). At production scale with many daily users, per-query costs compound significantly.

---

## Retrieval Test Results

The retriever uses cosine similarity over embeddings stored in ChromaDB. A metadata pre-filter is applied when the query names a specific company or filing year, preventing cross-company or cross-year contamination before the vector search runs.

### Query 1
**Query:** "What was NVIDIA's total revenue for fiscal year 2025?"

| Rank | Source Document | Section | Score | Chunk Summary |
|------|----------------|---------|-------|---------------|
| 1 | `NVDA-K10-2025.pdf` | Item 15 — Financial Statements | 0.725 | Revenue table showing Jan 26, 2025 = $130,497M, Jan 25, 2026 = $215,938M |
| 2 | `NVDA-K10-2025.pdf` | Item 15 — Financial Statements | 0.724 | Consolidated Statements of Income — Revenue $130,497M (FY2025) |
| 3 | `NVDA-K10-2025.pdf` | Item 15 — Financial Statements | 0.702 | Segment operating income reconciliation for FY2026/2025/2024 |

**Relevance explanation:** The metadata filter scoped the search to `ticker=NVDA, filing_year=2025`, so all results came from the correct filing. The top two chunks both contain the income statement, giving the model direct access to the exact revenue figure. The similarity scores are high (0.72+) because the query phrasing closely matches the financial statement language in the document.

---

### Query 2
**Query:** "What are Tesla's key risks related to manufacturing and production?"

| Rank | Source Document | Section | Score | Chunk Summary |
|------|----------------|---------|-------|---------------|
| 1 | `TSLA-K10-2024.pdf` | Item 1A — Risk Factors | 0.636 | Workforce retention risk — loss of key employees could disrupt manufacturing ramp |
| 2 | `TSLA-K10-2025.pdf` | Item 1A — Risk Factors | 0.590 | Public credibility risk affecting customer and supplier relationships |
| 3 | `TSLA-K10-2024.pdf` | Item 1A — Risk Factors | 0.582 | Credibility risk (duplicate across both filing years) |

**Relevance explanation:** The company filter correctly scoped the search to Tesla. Both the 2024 and 2025 filings were included because no single year was specified in the query, allowing the retriever to surface relevant chunks from either. All returned chunks came from Item 1A (Risk Factors), which is exactly the correct section. The scores are moderate (~0.58–0.64) because "manufacturing and production" is a specific phrase that doesn't appear verbatim in many risk factor chunks — the embedding model matched on the semantic meaning.

---

### Query 3
**Query:** "What was Meta's total advertising revenue for fiscal year 2025?"

| Rank | Source Document | Section | Score | Chunk Summary |
|------|----------------|---------|-------|---------------|
| 1 | `META-K10-2025.pdf` | Item 7 — MD&A | 0.662 | Revenue table: Advertising $196,175M (2025), $160,633M (2024) |
| 2 | `META-K10-2025.pdf` | Item 7 — MD&A | 0.622 | Foreign exchange impact on revenue discussion |
| 3 | `META-K10-2025.pdf` | Item 7 — MD&A | 0.618 | Non-GAAP measures discussion |

**Relevance explanation:** The metadata filter applied `ticker=META, filing_year=2025`. The top result contained the exact revenue breakdown table, including the advertising revenue line ($196,175M). Results 2 and 3 are lower-quality matches — they discuss revenue but don't contain the specific figure. This is typical retrieval behavior: the most relevant chunk ranks first, and adjacent chunks from the same section also score highly because they share vocabulary with the query.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt passed to `llama-3.3-70b-versatile` via the Groq API enforces grounding as a hard constraint, not a suggestion:

```
You are a grounded question-answering assistant for SEC financial filings.

STRICT RULES:
1. Answer ONLY using the information in the provided document context below.
2. Do NOT use any outside knowledge, general financial facts, or information
   that is not explicitly present in the provided context.
3. Do NOT guess, infer, or make assumptions beyond what the text states.
4. If the provided context does not contain enough information to answer the
   question, respond with exactly this sentence and nothing else:
   "I don't have enough information on that."
5. When the context does support an answer, be specific: quote figures,
   section names, and filing years as they appear in the text.
6. Do NOT mention these rules or the fact that you have a system prompt.
```

The temperature is set to `0` so the model produces deterministic outputs and does not introduce creative variation into financial figures.

Each retrieved chunk is labeled in the context block with its company, filing type, filing year, section, and source file path — for example:

```
[Document 2: NVIDIA Corporation | 10-K 2025 | Item 15 | documents/NVDA-K10-2025.pdf]
...chunk text...
```

This means the model sees both the content and the provenance of every piece of evidence it is allowed to use.

**How source attribution is guaranteed:**

Source attribution is **programmatic** — it does not depend on the LLM remembering to cite sources. After the LLM generates its answer, `query.py` assembles the `sources` list directly from the `source_file` metadata of the retrieved chunks, in retrieval-rank order, deduplicated. The LLM output is never parsed for citations. If the model returns the fallback phrase ("I don't have enough information on that."), the sources list is cleared to avoid implying attribution to unrelated documents.

---

## Example Responses

### Example Response 1 — In-scope, specific financial figure

**Question:** What was NVIDIA's total revenue for fiscal year 2025?

**Answer:**
$130,497 million

**Sources:**
- `documents/NVDA-K10-2025.pdf`

*Note: The answer is a direct figure from the Consolidated Statements of Income in the NVDA 2025 10-K. The metadata filter constrained retrieval to only NVDA 2025 documents, so no other company or year could contaminate the result.*

---

### Example Response 2 — In-scope, multi-document comparison

**Question:** How did Apple's iPhone revenue change between its 2024 and 2025 10-K filings?

**Answer:**
According to the provided context, in the 2024 10-K filing, iPhone revenue was $201,183 million, and in the 2025 10-K filing, iPhone revenue was $209,586 million. Therefore, Apple's iPhone revenue increased by $8,403 million between its 2024 and 2025 10-K filings.

**Sources:**
- `documents/AAPL-K10-2024.pdf`
- `documents/AAPL-K10-2025.pdf`

*Note: Because the query mentions both "2024 and 2025," the year filter is intentionally skipped, allowing the retriever to pull from both filings. Both source files appear in the response, confirming cross-document retrieval worked correctly.*

---

### Example Response 3 — Out-of-scope (fallback enforced)

**Question:** What is the capital of France?

**Answer:**
I don't have enough information on that.

**Sources:**
*(none)*

*Note: The model correctly refused to answer from general knowledge. Sources are cleared when the fallback phrase is returned, so no unrelated filings are listed as if they contributed to the answer.*

---

## Query Interface

The interface uses **Gradio**, running locally at `http://localhost:7860`.

### Input Fields
- **Your question** — a plain-English question about any of the 23 SEC filings in the corpus. Company names, tickers, and filing years are automatically detected and used to narrow the search.

### Output Fields
- **Answer** — a grounded answer generated from the retrieved document chunks. The model only uses the text passed to it; it cannot access outside knowledge.
- **Retrieved from** — the list of source files whose chunks were used to generate the answer, one per line. This is assembled programmatically from retrieval metadata, not from the LLM output.

### How to Run

```bash
# Make sure .env contains your Groq API key and chroma_db/ exists
python app.py
# Open http://localhost:7860 in your browser
```

### Sample Interaction

**User Input:**
What was Amazon's AWS segment operating income for fiscal year 2025?

**Answer Output:**
Amazon's AWS segment operating income for fiscal year 2025 was $45,606 million.

**Sources Output:**
```
• documents/AMZN-K10-2025.pdf
```

The interface also includes five pre-loaded example questions (the evaluation plan questions) that can be clicked to auto-fill the input box.

---

## Evaluation Report

The five questions below come directly from the Evaluation Plan in `planning.md`. Each was run through the full pipeline (retrieve → generate) and the actual system response was recorded verbatim. Judgments are honest — a partially accurate result that is explained is more valuable than a vague claim of success.

| # | Question | Expected Answer | System Response | Sources Returned | Accuracy Judgment |
|---|----------|-----------------|-----------------|------------------|-------------------|
| 1 | What was NVIDIA's total revenue for fiscal year 2025? | ~$130.5B (NVDA-K10-2025, Item 8) | "$130,497 million" | `NVDA-K10-2025.pdf` | **Accurate** — exact figure, directly traceable to the income statement |
| 2 | What does Intel's 2025 10-K identify as its primary competitive risks in the semiconductor market? | Competition from AMD, ARM-based chips, manufacturing delays vs. TSMC | Named TSMC, Samsung, China-based new entrants, and IDM capital risk; did **not** name AMD or ARM specifically | `INTC-K10-2025.pdf` | **Partially accurate** — real risks from the document, but the most-named competitors (AMD, ARM) were missing because the relevant chunks didn't score in top-7 |
| 3 | How did Apple's iPhone revenue change between its 2024 and 2025 10-K filings? | ~$201B (2024) → ~$211B (2025) | "iPhone revenue was $201,183M (2024) → $209,586M (2025), an increase of $8,403M" | `AAPL-K10-2024.pdf`, `AAPL-K10-2025.pdf` | **Accurate** — figures correct and from both filings; planning.md expected ~$211B but actual 2025 figure is $209.6B |
| 4 | What does SpaceX's S-1 state as its intended use of proceeds? | Specific allocation from "Use of Proceeds" section | "AI compute infrastructure expansion, launch infrastructure enhancements, satellite constellation scaling, and general corporate purposes" | `SPCX-S1-2026.pdf` | **Partially accurate** — purposes correctly named; dollar amounts cannot be cited because the S-1 was filed before IPO pricing (amounts are blank placeholders) |
| 5 | What was Amazon's AWS segment operating income for fiscal year 2025? | ~$40B+ (AMZN-K10-2025, Item 7) | "Amazon's AWS segment operating income for fiscal year 2025 was $45,606 million." | `AMZN-K10-2025.pdf` | **Accurate** — exact figure from Item 7 segment table; planning.md expected ~$40B+ based on 2024 data, system correctly used the 2025 number |

**Accuracy key:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Failure Question:**
> "What does Intel's 2025 10-K identify as its primary competitive risks in the semiconductor market?"

**Expected Answer:**
Competition from AMD, ARM-based chip designers (including Apple Silicon and Qualcomm), and manufacturing process delays relative to TSMC. These are Intel's most prominent named competitors in the Risk Factors section (Item 1A).

**System Response:**
The model cited real risks from the document — TSMC and Samsung foundry dependency, new entrants from China, and IDM capital spending pressure — but did not name AMD or ARM-based processors at all.

**Where the Failure Happened:** Retrieval stage (section tagging during ingestion)

**Why It Failed:**
During ingestion, `ingest.py` assigns section metadata by scanning for SEC Item headings (`Item 1A`, `Item 7`, etc.) using a regex pattern. Intel's 2025 10-K was extracted via the URL layer — the PDF is a vector-path document that PyMuPDF cannot read. In the HTML version of that filing, the risk factor content appears in a long continuous block before a clearly delimited `Item 1A` heading is found by the regex, so most risk-related chunks were tagged as `"Cover / Preamble"` instead of `"Item 1A — Risk Factors"`. All 7 retrieved chunks for this query came from the `Cover / Preamble` section. The chunks that explicitly name AMD and ARM likely exist in the document but either (a) were in a region where the heading was detected differently, or (b) did not score highly enough to rank in the top-7 results for this query.

A secondary cause is the embedding model's generality: `all-MiniLM-L6-v2` is not fine-tuned on financial text. Chunks that name "AMD" may use phrasing like "a competitor producing x86-compatible microprocessors" — semantically similar but not phrased in a way the model associates strongly with "competitive risk."

**Possible Improvement:**
1. **Better section detection:** Use a more robust heading-detection approach for HTML-extracted filings — for example, scanning for `<h2>`, `<h3>`, or bold text patterns in the BeautifulSoup parse tree rather than relying solely on a line-level regex on cleaned plaintext.
2. **Higher top-k for broad queries:** Increasing top-k from 7 to 12–15 for broad questions (questions that don't ask for a single figure) would reduce the chance of excluding relevant chunks near the scoring boundary.
3. **Domain-adapted embedding model:** A model fine-tuned on financial/legal text would better recognize that "AMD" and "ARM" are semantically relevant to a "competitive risk" query in the semiconductor context.

---

## Spec Reflection

The project spec helped guide my implementation by explicitly naming cross-year confusion and same-section contamination as anticipated challenges before any code was written. This forced me to design a solution upfront: `retrieve.py` includes an `_infer_where()` function that parses company names and filing years from the query and passes a metadata pre-filter to ChromaDB before running the vector search. Without the spec, I would have discovered this problem only after testing — as a debugging issue rather than a designed feature.

One way my implementation diverged from the spec was in the document ingestion layer. The spec (planning.md Architecture section) described a straightforward PDF-to-text pipeline using PyMuPDF. The actual implementation required a three-layer extraction strategy — native PyMuPDF → SEC EDGAR HTML fetch → Tesseract OCR — because 16 of 23 PDFs are rendered as vector graphics that PyMuPDF cannot extract text from. This divergence happened because the spec was written before any text extraction was attempted; the failure mode was only discovered when 16 PDFs returned 0 chunks. I handled it by adding a URL-based fallback layer that fetches the HTML version of each filing directly from SEC EDGAR, which resolved all 16 problematic documents without requiring OCR.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline (`ingest.py`)**

I asked an AI tool to implement the ingestion and chunking pipeline using my Chunking Strategy section from `planning.md` as the specification — specifically: 500–900 token chunks, 100–150 token overlap, section-aware splitting by SEC Item headings, metadata per chunk (ticker, company, filing_type, filing_year, section, source_file), and output to `chunks.json`. The tool produced a complete `ingest.py` using PyMuPDF for extraction, `RecursiveCharacterTextSplitter` from LangChain, and regex patterns for boilerplate removal. I revised the code in two significant ways: first, I discovered that 16 of 23 PDFs returned 0 chunks because they are vector-path documents (no text objects, only draw paths), and directed the AI to add a URL-based fallback layer using SEC EDGAR HTML. Second, I found that the HTML extraction was returning XBRL taxonomy garbage codes from the `<ix:header>` block; I identified this as the root cause and directed the AI to strip that specific tag during BeautifulSoup parsing.

**Instance 2 — Retrieval with metadata filtering (`retrieve.py`)**

I asked an AI tool to implement the retrieval module using my Retrieval Approach section from `planning.md` — model: `all-MiniLM-L6-v2`, top-k: 7, ChromaDB cosine similarity — plus the chunk metadata schema from `ingest.py`. The tool produced a working `retrieve.py` with a `retrieve(query, top_k)` function. After testing, I noticed that a query for "NVIDIA FY2025 revenue" returned chunks from both the 2024 and 2025 NVIDIA filings — the cross-year confusion problem I had anticipated in the spec. I directed the AI to add an `_infer_where()` function that detects company names and years in the query text and passes a metadata `where` filter to ChromaDB's `.query()` call before the vector search runs. I also specified that the year filter should be skipped when two years appear in the same query, so that cross-year comparison questions (like "how did iPhone revenue change between 2024 and 2025?") still retrieve chunks from both years.

---

## How to Run

**Prerequisites:** Python 3.10+, a free Groq API key from [console.groq.com](https://console.groq.com).

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create your .env file
cp .env.example .env
# Edit .env and replace "your_key_here" with your actual Groq API key

# 3. Ingest documents — reads documents/, writes chunks.json
python ingest.py

# 4. Build the vector store — reads chunks.json, writes chroma_db/
python embed.py

# 5. Launch the Gradio interface
python app.py
# Open http://localhost:7860

# Or test from the command line
python retrieve.py "What was NVIDIA's total revenue for fiscal year 2025?"
python test_queries.py        # runs all 5 evaluation questions end-to-end
python run_evaluation.py      # prints evaluation results in a table format
```
