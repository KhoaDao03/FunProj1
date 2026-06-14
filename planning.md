# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

My system covers SEC company filing documents, specifically Form 10-K annual reports and Form S-1 registration statements. This knowledge is valuable because these filings contain important information about a company’s business model, risks, revenue, financial condition, management discussion, legal issues, IPO plans, and future uncertainties. However, this information is hard to find quickly through official channels because SEC filings are very long, dense, and written in formal legal and financial language. A user may need to search across many pages and sections just to answer one question, such as “What are this company’s biggest risks?” or “How does the company make money?”

This domain is useful for students, investors, analysts, and anyone trying to understand public companies or IPO candidates without manually reading hundreds of pages. My system will make these documents easier to search by allowing users to ask plain-English questions and retrieve the most relevant parts of the filings.

---
## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | File path | Original SEC URL |
|---|--------|------|-----------|------------------|
| 1 | Apple Inc. Annual Report | SEC Form 10-K | documents/AAPL-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm |
| 2 | Amazon.com, Inc. Annual Report | SEC Form 10-K | documents/AMZN-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm |
| 3 | Broadcom Inc. Annual Report | SEC Form 10-K | documents/AVGO-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm |
| 4 | Alphabet Inc. Annual Report | SEC Form 10-K | documents/GOOG-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm |
| 5 | Intel Corporation Annual Report | SEC Form 10-K | documents/INTC-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/50863/000005086326000011/intc-20251227.htm |
| 6 | Meta Platforms, Inc. Annual Report | SEC Form 10-K | documents/META-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm |
| 7 | Microsoft Corporation Annual Report | SEC Form 10-K | documents/MSFT-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm |
| 8 | Micron Technology, Inc. Annual Report | SEC Form 10-K | documents/MU-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/mu-20250828.htm |
| 9 | NVIDIA Corporation Annual Report | SEC Form 10-K | documents/NVDA-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm |
| 10 | Space Exploration Technologies Corp. Registration Statement | SEC Form S-1 | documents/SPCX-S1-2026.pdf | https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm |
| 11 | Tesla, Inc. Annual Report | SEC Form 10-K | documents/TSLA-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm |
| 12 | Netflix, Inc. Annual Report | SEC Form 10-K | documents/NFLX-K10-2025.pdf | https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm |
| 13 | Apple Inc. Annual Report | SEC Form 10-K | documents/AAPL-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm |
| 14 | Amazon.com, Inc. Annual Report | SEC Form 10-K | documents/AMZN-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm |
| 15 | Broadcom Inc. Annual Report | SEC Form 10-K | documents/AVGO-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1730168/000173016824000139/avgo-20241103.htm |
| 16 | Alphabet Inc. Annual Report | SEC Form 10-K | documents/GOOG-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm |
| 17 | Intel Corporation Annual Report | SEC Form 10-K | documents/INTC-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/50863/000005086325000009/intc-20241228.htm |
| 18 | Meta Platforms, Inc. Annual Report | SEC Form 10-K | documents/META-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm |
| 19 | Microsoft Corporation Annual Report | SEC Form 10-K | documents/MSFT-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/789019/000095017024087843/msft-20240630.htm |
| 20 | Micron Technology, Inc. Annual Report | SEC Form 10-K | documents/MU-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/723125/000072312524000027/mu-20240829.htm |
| 21 | NVIDIA Corporation Annual Report | SEC Form 10-K | documents/NVDA-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/nvda-20240128.htm |
| 22 | Tesla, Inc. Annual Report | SEC Form 10-K | documents/TSLA-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm |
| 23 | Netflix, Inc. Annual Report | SEC Form 10-K | documents/NFLX-K10-2024.pdf | https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->


**Chunk size:**

I used a section-aware chunking strategy with chunks of about 500–900 tokens each. SEC filings are much longer than normal webpages and often include dense paragraphs, financial tables, legal risk disclosures, and repeated language. A chunk that is too small may lose important context, while a chunk that is too large may make retrieval less precise. A 500–900 token range gives each chunk enough context to include a complete paragraph group or subsection while still being specific enough for search.

**Overlap:**

I used an overlap of about 100–150 tokens between chunks. Overlap is important for SEC filings because key ideas often continue across paragraph boundaries. For example, a risk factor may begin in one paragraph and explain the actual business impact in the next paragraph. The overlap helps prevent important context from being cut off between two chunks.

**Why these choices fit your documents:**

These documents are long, formal, and highly structured. They are not short reviews or casual posts. Most filings have clear section headings such as Business, Risk Factors, Management’s Discussion and Analysis, Financial Statements, Legal Proceedings, Use of Proceeds, and Executive Compensation. Because of this structure, I first split the documents by major headings or item numbers when possible. Then, if a section was still too long, I split it into smaller overlapping chunks.

This approach fits the domain better than simple fixed-size chunking because the section titles carry important meaning. For example, the phrase “competition” could appear in several parts of a filing, but it means something different inside the Business section compared to the Risk Factors section. Keeping section metadata with each chunk helps the system retrieve more relevant answers.

Before chunking, I removed unnecessary HTML tags, repeated page navigation text, table-of-contents noise, and extra whitespace. I also kept useful metadata such as company name, filing type, filing year, section title, and source URL. This metadata makes it easier to trace answers back to the original filing and helps users understand where the answer came from.

**Final chunk count:** *(to be filled in after running `ingest.py`)*

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` — free, runs locally, and fast enough for a prototype over 23 documents.

**Top-k:** 7 — SEC filings are dense and a single question (e.g. "what are the risks?") often spans multiple subsections, so retrieving more chunks reduces the chance of missing relevant context.

**Production tradeoff reflection:**

- **Accuracy:** A stronger embedding model (e.g. `text-embedding-3-large` or a finance-tuned model) would better understand formal financial language. Questions like "How did liquidity risk change year-over-year?" rely on understanding subtle semantic distinctions that `all-MiniLM-L6-v2` may conflate. The tradeoff is cost and latency.

- **Domain-specific language:** SEC filings use specialized terminology — *material weakness*, *going concern*, *revenue recognition*, *operating lease liabilities*, *regulatory exposure*. A general-purpose embedding model may not represent these terms precisely. In production, a model fine-tuned on legal or financial text (e.g. `FinBERT`-family embeddings) would improve retrieval quality for domain-specific queries.

- **Latency:** `all-MiniLM-L6-v2` is fast because it is small (22M parameters). Larger models produce higher-quality embeddings but add per-query latency. For a real user-facing product, retrieval speed directly impacts user experience.

- **Cost:** Local embedding models have no per-query cost. API-based models (e.g. OpenAI embeddings) charge per token for both ingestion and querying. At production scale, the cost of embedding thousands of chunks and serving many daily queries would factor significantly into model selection.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What was NVIDIA's total revenue for fiscal year 2025? | ~$130.5 billion. Verify exact figure in NVDA-K10-2025.pdf → Item 7 (MD&A) or Item 8 (Financial Statements). Tests retrieval of a specific number from a dense financial table. |
| 2 | What does Intel's 2025 10-K identify as its primary competitive risks in the semiconductor market? | Should mention competition from AMD and ARM-based chips, loss of market share in PC and data center CPUs, and manufacturing process delays relative to TSMC. Verify in INTC-K10-2025.pdf → Item 1A (Risk Factors). Tests whether section-level chunking preserves Risk Factors context. |
| 3 | How did Apple's iPhone revenue change between its 2024 and 2025 10-K filings? | iPhone revenue was ~$201B in FY2024 and ~$211B in FY2025. Verify exact figures in AAPL-K10-2024.pdf and AAPL-K10-2025.pdf → Item 7 (MD&A, segment revenue table). Tests multi-document retrieval across two filings without confusing the years. |
| 4 | According to SpaceX's S-1 registration statement, what does the company state as its intended use of proceeds from the offering? | Look for specific allocation in the "Use of Proceeds" section near the front of SPCX-S1-2026.pdf. Verify exact language from the PDF. Tests retrieval from the only S-1 in the corpus — a section type that does not exist in 10-K filings. |
| 5 | What was Amazon's AWS segment operating income for fiscal year 2025? | ~$40B+ (verify exact figure in AMZN-K10-2025.pdf → Item 7 MD&A, segment results). Tests precision — the question asks for operating income specifically, not revenue or net income, so retrieval of the wrong AWS metric counts as a failure. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Chunking across financial tables:** SEC filings embed multi-column tables for financial statements such as revenue by segment, balance sheets, and income statements. When PDFs are converted to plain text, these tables lose their column alignment and headers. A chunk may contain a string like `"42,001 38,120 29,555"` with no labels indicating what those numbers represent. This makes it impossible for the embedding model to understand the financial meaning, causing retrieval to fail for specific financial metric questions.

2. **Same section name, different meaning across companies:** Every 10-K in the corpus has a "Risk Factors" section, a "Business" section, and an "MD&A" section. When a user asks a general question like "what are the risks?", retrieval may return chunks from multiple companies' Risk Factors sections rather than the intended one. Without strong metadata filtering on company name, cross-company contamination will produce blended or irrelevant answers.

3. **Cross-year confusion from duplicate companies:** The corpus contains two filings for the same company in consecutive years (e.g., AAPL-K10-2024 and AAPL-K10-2025). A question like "What was Apple's revenue?" could retrieve chunks from both years and return a contradictory or blended answer. The system must either detect the year from the query or clearly label which filing year each retrieved chunk came from.

4. **Boilerplate diluting retrieval quality:** SEC filings contain large blocks of standard legal boilerplate — forward-looking statement disclaimers, standard audit language, cover page text, and repeated table-of-contents entries. These chunks may score highly for common query terms while carrying no useful information, pushing genuinely relevant chunks out of the top-k results.

5. **SpaceX S-1 structural mismatch:** The corpus contains 22 Form 10-K filings and one Form S-1 (SpaceX). The S-1 includes sections like "Use of Proceeds," "Dilution," and "Underwriting" that do not exist in any 10-K. For S-1-specific questions, there is only one document to retrieve from. If that document was not chunked or embedded correctly, there is no fallback, making failures on S-1 questions unrecoverable.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌─────────────────────┐     ┌──────────────────────────┐      ┌────────────────────────────┐
│  Document Ingestion │───▶│         Chunking          │────▶│  Embedding + Vector Store  │
│                     │     │                           │     │                            │
│  PyMuPDF (fitz)     │     │  LangChain                │     │  sentence-transformers     │
│  - Load 23 PDFs     │     │  RecursiveCharacter       │     │  all-MiniLM-L6-v2          │
│  - Extract raw text │     │  TextSplitter             │     │                            │
│  - Strip boilerplate│     │  + section-aware splits   │     │  ChromaDB                  │
│  - Tag metadata:    │     │  500–900 tokens           │     │  - Store embeddings        │
│    company, year,   │     │  100–150 token overlap    │     │  - Store chunk text        │
│    filing type,     │     │  Split by Item headings   │     │  - Store metadata          │
│    section title    │     │  first, then by size      │     │                            │
└─────────────────────┘     └──────────────────────────┘     └────────────────────────────┘
                                                                            │
                                                                            ▼
                             ┌──────────────────────────┐     ┌────────────────────────────┐
                             │       Generation          │◀─── │         Retrieval          │
                             │                           │     │                            │
                             │  Grok API                 │     │  ChromaDB cosine similarity│
                             │ (llama-3.3-70b-versatile) │     │  top-k = 7                 │
                             │  - Build prompt with      │     │  - Embed user query        │
                             │    retrieved chunks       │     │  - Return top 7 chunks     │
                             │  - Return grounded answer │     │    with metadata           │
                             │  - Cite source filing     │     │                            │
                             └──────────────────────────┘     └────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

- **Tool:** Claude, Codex
- **Input:** The Chunking Strategy section of this planning.md (chunk size 500–900 tokens, overlap 100–150 tokens, section-aware splitting by Item headings), plus the Document Sources table (23 PDFs, mix of 10-K and S-1)
- **Expected output:** An `ingest.py` script that loads each PDF using PyMuPDF, strips boilerplate text (table of contents, page headers, forward-looking disclaimers), splits by Item/section headings first then falls back to RecursiveCharacterTextSplitter, and attaches metadata (company name, filing type, filing year, section title, source file path) to each chunk
- **Verification:** Print the total chunk count across all 23 documents, print 3 sample chunks with their metadata, and confirm that chunks from different sections of the same filing carry distinct section titles in their metadata

**Milestone 4 — Embedding and retrieval:**

- **Tool:** Claude, Codex
- **Input:** The Retrieval Approach section of this planning.md (embedding model: all-MiniLM-L6-v2, top-k: 7), plus the output schema of `ingest.py` (chunk text + metadata dict)
- **Expected output:** An `embed.py` script that loads all chunks, generates embeddings using sentence-transformers, and stores them in ChromaDB with metadata. A `retrieve.py` script that takes a plain-English query, embeds it, runs cosine similarity search, and returns the top 7 chunks with their text and metadata
- **Verification:** Run the 5 evaluation questions from this planning.md through `retrieve.py` and confirm that the returned chunks come from the correct company and section — not from a different company's filing or the wrong year

**Milestone 5 — Generation and interface:**

- **Tool:** Claude, Codex
- **Input:** The Architecture diagram from this planning.md (retrieval → prompt construction → Claude API call), the Evaluation Plan table (5 test questions with expected answers), and the `retrieve.py` output schema
- **Expected output:** A `generate.py` script that takes a user query, calls `retrieve.py` to get top-7 chunks, builds a prompt that includes the retrieved chunks and instructs the model to answer only from the provided context and cite the source filing, calls the Claude API, and returns the answer with source attribution. A simple CLI or Gradio interface for interactive querying
- **Verification:** Run all 5 evaluation questions end-to-end, compare answers against the expected answers in the Evaluation Plan, and confirm each answer cites the correct source document and filing year
