"""
test_queries.py — End-to-end grounded generation tests

Runs the 5 evaluation questions from planning.md plus one out-of-scope question
to verify the "I don't have enough information on that." fallback.

Usage:
    python test_queries.py

Requirements:
    - embed.py must have been run (chroma_db/ must exist)
    - .env must contain GROQ_API_KEY=your_key_here

What each test checks
---------------------
    1. Answer is non-empty
    2. Sources list is non-empty (grounding is traceable)
    3. The answer does NOT trigger the "not enough information" fallback
       (meaning relevant chunks were actually retrieved and used)

    The out-of-scope test inverts rule 3:
    4. The system says "I don't have enough information on that."
       when the corpus cannot answer the question.
"""

from query import ask

# ── Test cases ────────────────────────────────────────────────────────────────

IN_SCOPE_QUESTIONS = [
    {
        "id": "Q1",
        "question": "What was NVIDIA's total revenue for fiscal year 2025?",
        "note": "Expect ~$130.5B; verify in NVDA-K10-2025 Item 8",
    },
    {
        "id": "Q2",
        "question": "What does Intel's 2025 10-K identify as its primary competitive risks in the semiconductor market?",
        "note": "Expect mention of AMD, TSMC, ARM; verify in INTC-K10-2025 Item 1A",
    },
    {
        "id": "Q3",
        "question": "How did Apple's iPhone revenue change between its 2024 and 2025 10-K filings?",
        "note": "Expect ~$201B (2024) → ~$209B (2025); two filings in sources",
    },
    {
        "id": "Q4",
        "question": "According to SpaceX's S-1 registration statement, what is the intended use of proceeds from the offering?",
        "note": "Expect use-of-proceeds language; source must be SPCX-S1-2026",
    },
    {
        "id": "Q5",
        "question": "What was Amazon's AWS segment operating income for fiscal year 2025?",
        "note": "Expect ~$45.6B; verify in AMZN-K10-2025 Item 7",
    },
]

OUT_OF_SCOPE_QUESTION = {
    "id": "Q6",
    "question": "What is the capital of France?",
    "note": "Not in any SEC filing — expect 'I don't have enough information on that.'",
}

FALLBACK_PHRASE = "I don't have enough information on that."

# ── Runner ────────────────────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    print("=" * 70)
    print("SEC Filings RAG — End-to-end generation tests")
    print("=" * 70)

    # In-scope tests
    for tc in IN_SCOPE_QUESTIONS:
        print(f"\n{tc['id']}: {tc['question']}")
        print(f"     Note: {tc['note']}")

        result  = ask(tc["question"])
        answer  = result["answer"]
        sources = result["sources"]

        ok = True

        if not answer:
            print("  FAIL — empty answer")
            ok = False

        if FALLBACK_PHRASE.lower() in answer.lower():
            print(f"  FAIL — got fallback phrase instead of a grounded answer")
            ok = False

        if not sources:
            print("  FAIL — no sources returned (grounding not traceable)")
            ok = False

        if ok:
            print(f"  PASS")
            print(f"  Answer   : {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"  Sources  : {', '.join(sources)}")
            passed += 1
        else:
            print(f"  Answer   : {answer[:200]}")
            print(f"  Sources  : {sources}")
            failed += 1

    # Out-of-scope test
    print(f"\n{OUT_OF_SCOPE_QUESTION['id']}: {OUT_OF_SCOPE_QUESTION['question']}")
    print(f"     Note: {OUT_OF_SCOPE_QUESTION['note']}")

    result = ask(OUT_OF_SCOPE_QUESTION["question"])
    answer = result["answer"]

    if FALLBACK_PHRASE.lower() in answer.lower():
        print(f"  PASS — system correctly declined to answer")
        passed += 1
    else:
        print(f"  FAIL — model answered a question not in corpus (hallucination risk)")
        print(f"  Answer: {answer[:200]}")
        failed += 1

    # Summary
    total = passed + failed
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} passed")
    if failed:
        print("Review FAIL items above — a grounded response must be traceable")
        print("to retrieved text; any answer without sources is a failure.")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
